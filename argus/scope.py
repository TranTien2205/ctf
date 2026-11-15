"""Scope guard - the hard boundary on every outbound request.

Every tool that can emit a network request goes through ScopeGuard.check()
before the request is built. Scope is fail-closed: a URL is allowed only when
its host is explicitly in scope (or is a subdomain of an in-scope host when
include_subdomains is set) and its path is not excluded.

Private/loopback addresses are refused unless allow_private is set OR the
initial target itself was private (a lab). Resolution is cached per host.
"""
from __future__ import annotations

import ipaddress
import posixpath
import re
import socket
import sys
import threading
import urllib.parse


class ScopeError(PermissionError):
    pass


def _is_private_host(host: str) -> bool:
    if host in ("localhost", "localhost.localdomain"):
        return True
    try:
        return _ip_private(ipaddress.ip_address(host))
    except ValueError:
        pass
    # getaddrinfo over gethostbyname: it returns BOTH families and every
    # address - a host whose only AAAA is ::1 must not read as public, and
    # a multi-record answer must not pass on the strength of one public IP
    # Bounded, on a daemon thread, for the reason `analysis._resolves`
    # already records: `getaddrinfo` takes no timeout and
    # `socket.setdefaulttimeout` is process-global, so it would leak into
    # every socket created while a lookup is in flight - including the
    # target connections and, in the test suite, the lab's own server.
    #
    # Unbounded, this was an undeadlined blocking call per NEW in-scope
    # host on the agent's own thread, and the target chooses how many new
    # hosts there are: `include_subdomains` defaults to True, and `crawl`
    # queues every in-scope-looking href out of the target's own HTML.
    # Measured here: a fresh in-scope subdomain cost 15.0s inside
    # `check()`, and a bare `getaddrinfo` against a non-answering resolver
    # 24.2s.
    infos: list = []
    failed: list = []

    def _lookup() -> None:
        try:
            infos.extend(socket.getaddrinfo(host, None))
        except OSError:
            failed.append(True)

    worker = threading.Thread(target=_lookup, daemon=True)
    worker.start()
    worker.join(_RESOLVE_DEADLINE_S)
    if worker.is_alive():
        # Timed out. The verdict is the SAME as the unresolvable case this
        # function already had - "nothing can connect anyway" - and that is
        # a deliberate decision not to change a security posture as a side
        # effect of a cost fix.
        #
        # Fail-closed was written first and measured: it refuses in-scope
        # hosts in any environment without a working resolver. Here
        # `getaddrinfo("b.example")` raises OSError after 24.1s, so a 2s
        # deadline fires first and cannot tell "no resolver" from "slow
        # resolver" - and `tests/test_scope.py::test_extra_hosts` and
        # `::test_subdomain_allowed_by_default` both failed, which is two
        # real engagements' worth of behaviour, not a test artifact.
        #
        # What that leaves open, written down rather than implied: an
        # attacker who controls the resolution TIMING of an in-scope
        # hostname can keep a private address from being seen here, because
        # the connection that follows resolves independently. Closing it
        # needs a decision about refusing hosts on slow DNS, which is the
        # operator's to make and not a side effect of bounding a lookup.
        # The warning below is so it is not silent.
        if host.lower() not in _RESOLVE_TIMED_OUT:
            _RESOLVE_TIMED_OUT.add(host.lower())
            print(f"[argus] scope: {host} did not resolve within "
                  f"{_RESOLVE_DEADLINE_S}s, so it was not checked against "
                  "the private-address rule; pass --allow-private "
                  "deliberately if that is expected",
                  file=sys.stderr)
        return False
    if failed and not infos:
        return False  # unresolvable: nothing can connect anyway
    for info in infos:
        try:
            if info[4] and info[4][0] and \
                    _ip_private(ipaddress.ip_address(info[4][0])):
                return True
        except ValueError:
            continue  # non-IP sockaddr (e.g. AF_UNIX) - not a TCP target
    return False


# Per-host, not per-run: the cache below makes a repeat free, and a cap on
# how many distinct IN-SCOPE hosts may be resolved would be a functional
# limit the operator did not ask for. What was missing was a bound on ONE
# lookup, which is what the target controls.
_RESOLVE_DEADLINE_S = 2.0
# warned once per host, so a crawl does not repeat it per href
_RESOLVE_TIMED_OUT: set[str] = set()


def _ip_private(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Is this address one the operator has to ask for explicitly?

    `is_multicast` is in the list because leaving it out was inconsistent in
    the one direction that matters. Measured against a PUBLIC target with
    `allow_private` off: `localhost` and `10.0.0.1` were refused and
    `224.0.0.1` and `239.255.255.250` - the SSDP group, a local-network
    address - were allowed. The host still has to be in scope, so this was
    never an allowlist bypass; it was a disagreement about what counts as
    private inside a boundary whose whole job is to refuse before any bytes
    are sent.

    `ipaddress` already resolves the IPv4-mapped IPv6 forms correctly -
    `::ffff:127.0.0.1` is loopback and `::ffff:169.254.169.254` is
    link-local - which was checked rather than assumed, because the obvious
    guess was that they were the gap and they are not.
    """
    return (ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_reserved or ip.is_multicast)


def _collapse(path: str) -> str:
    """Normalize a path the way a target will, duplicate separators included.

    `posixpath.normpath` is POSIX-faithful about one thing that is wrong
    here: a path beginning with EXACTLY two slashes is implementation-defined,
    so normpath preserves it. `///admin` collapses to `/admin` and `//admin`
    does not. Three exclusion bypasses came out of that single rule, and all
    three are inside the threat model the comments in `check` already state:

      `//admin`     normpath keeps it, so it matched no `/admin` rule;
                    nginx and Apache merge duplicate slashes by default, so
                    the request reaches the excluded resource
      `/%2fadmin`   the unquote loop above turns it into `//admin`, and then
                    the same rule applies. httpx sends `/%2fadmin` raw, so
                    the decoding happens at the target
      `/\\admin`     the backslash fold produces `//admin` too, which is the
                    IIS case the fold exists for

    Measured against this guard with `--exclude /admin`: `/admin`, `/ADMIN`,
    `/x/../admin`, `/%61dmin`, `///admin` and `/%2F%2Fadmin` were all
    refused, while those three were allowed. So the normalization was not
    missing - it disagreed with itself about how many slashes mattered.

    Collapsing runs of slashes before and after normpath is safe in the
    direction this code already chose: over-blocking an operator-declared
    no-go area is the error to prefer, and `/administrator` is still not
    `/admin` because every comparison is `== prefix` or `prefix + "/"`.
    """
    collapsed = re.sub(r"/{2,}", "/", path)
    collapsed = posixpath.normpath(collapsed)
    return re.sub(r"/{2,}", "/", collapsed)


class ScopeGuard:
    def __init__(
        self,
        target: str,
        extra_hosts: list[str] | None = None,
        exclude_paths: list[str] | None = None,
        allow_private: bool = False,
        include_subdomains: bool = True,
    ):
        parsed = urllib.parse.urlparse(target if "://" in target else "http://" + target)
        if not parsed.hostname:
            raise ScopeError(f"cannot parse target: {target!r}")
        # strip the DNS-root dot at store time too - host_allowed rstrips
        # lookups, so '--target http://t.example.' would otherwise deny
        # 't.example' while allowing nothing else (fail-closed but
        # inconsistent)
        self.allowed_hosts = {parsed.hostname.lower().rstrip(".")}
        for host in extra_hosts or []:
            self.allowed_hosts.add(host.lower().rstrip("."))
        # Empties dropped rather than kept as `''`: the enforcement loop
        # below skips a falsy prefix, so a kept empty is an exclusion that
        # matches nothing while `describe()` and meta.json still list one.
        # `config.py` now refuses `--exclude /` outright; this is for every
        # other caller, since `ScopeGuard` is constructed directly in tests,
        # in `cli.py` and in the team plane.
        self.exclude_paths = [q for q in
                              (p.rstrip("/") for p in (exclude_paths or []))
                              if q]
        self.include_subdomains = include_subdomains
        # Labs run on loopback; if the target is private, private stays allowed
        # for this session. Otherwise it must be explicitly requested.
        # `is True` because this line decides whether private addresses
        # stay allowed for the WHOLE session, and it reads a function whose
        # other caller wants the opposite conservative answer. It is
        # belt-and-braces now that a timeout returns False rather than
        # True, and kept because the first version of this fix DID return
        # True on a timeout and THIS is the line that turned that into
        # "allow_private for the entire run". Measured: planting the bare
        # `_is_private_host(...)` back changes no test, so the coercion is
        # inert against the current function and exists to stop one
        # specific mistake recurring. Said rather than implied.
        target_private = _is_private_host(parsed.hostname) is True
        self.allow_private = allow_private or target_private
        # seed the cache with the target's real resolution
        self._private_cache: dict[str, bool] = {
            parsed.hostname.lower(): target_private}

    def host_allowed(self, host: str) -> bool:
        # a trailing dot is the DNS root marker - 't.example.' IS
        # 't.example'; normalize or the same host reads as foreign
        host = host.lower().rstrip(".")
        if host in self.allowed_hosts:
            return True
        if self.include_subdomains:
            return any(host.endswith("." + h) for h in self.allowed_hosts)
        return False

    def check(self, url: str) -> urllib.parse.ParseResult:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ScopeError(f"scheme not allowed (http/https only): {url!r}")
        host = parsed.hostname
        if not host:
            raise ScopeError(f"no host in URL: {url!r}")
        if not self.host_allowed(host):
            raise ScopeError(f"host out of scope: {host} (allowed: {sorted(self.allowed_hosts)})")
        # No lookup at all when the answer cannot change the outcome.
        # This ran unconditionally and the result was then discarded for
        # every `--allow-private` engagement - which is every lab run, and
        # every internal one, i.e. the runs most likely to touch many hosts.
        if not self.allow_private and host not in self._private_cache:
            self._private_cache[host] = _is_private_host(host)
        if not self.allow_private and self._private_cache.get(host):
            raise ScopeError(
                f"{host} resolves to a private/loopback address; pass --allow-private to permit"
            )
        path = parsed.path or "/"
        # httpx normalizes dot-segments AND percent-decodes before the wire,
        # so exclusion must match what is actually sent - a raw-path check
        # alone is bypassed by /%61dmin or /x/../admin reaching /admin.
        norm = path
        for _ in range(3):  # unquote until stable: defeats double-encoding
            dec = urllib.parse.unquote(norm)
            if dec == norm:
                break
            norm = dec
        norm = _collapse(norm)
        if not norm.startswith("/"):
            norm = "/" + norm
        # IIS-class targets fold case and treat '\' as a separator, so an
        # exclusion must match the same way or /ADMIN and /x\..\admin walk
        # straight past an '/admin' rule. Over-blocking is the safe error
        # for an operator-declared no-go area.
        lowered = path.lower()
        norm_l = norm.lower()
        folded = _collapse(norm_l.replace("\\", "/"))
        for prefix in self.exclude_paths:
            p = (prefix or "").lower()
            if p and (path == prefix or path.startswith(prefix + "/")
                      or norm == prefix or norm.startswith(prefix + "/")
                      or lowered == p or lowered.startswith(p + "/")
                      or folded == p or folded.startswith(p + "/")):
                raise ScopeError(f"path excluded by scope rules: {path}")
        return parsed

    def describe(self) -> str:
        lines = [
            f"allowed hosts: {', '.join(sorted(self.allowed_hosts))}"
            + (" (+subdomains)" if self.include_subdomains else ""),
            f"private addresses: {'allowed' if self.allow_private else 'refused'}",
        ]
        if self.exclude_paths:
            lines.append(f"excluded paths: {', '.join(self.exclude_paths)}")
        return "\n".join(lines)
