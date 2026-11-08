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
import socket
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
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return False  # unresolvable: nothing can connect anyway
    for info in infos:
        try:
            if info[4] and info[4][0] and \
                    _ip_private(ipaddress.ip_address(info[4][0])):
                return True
        except ValueError:
            continue  # non-IP sockaddr (e.g. AF_UNIX) - not a TCP target
    return False


def _ip_private(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved


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
        self.allowed_hosts = {parsed.hostname.lower()}
        for host in extra_hosts or []:
            self.allowed_hosts.add(host.lower())
        self.exclude_paths = [p.rstrip("/") for p in (exclude_paths or [])]
        self.include_subdomains = include_subdomains
        # Labs run on loopback; if the target is private, private stays allowed
        # for this session. Otherwise it must be explicitly requested.
        target_private = _is_private_host(parsed.hostname)
        self.allow_private = allow_private or target_private
        # seed the cache with the target's real resolution
        self._private_cache: dict[str, bool] = {
            parsed.hostname.lower(): target_private}

    def host_allowed(self, host: str) -> bool:
        host = host.lower()
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
        if host not in self._private_cache:
            self._private_cache[host] = _is_private_host(host)
        if self._private_cache[host] and not self.allow_private:
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
        norm = posixpath.normpath(norm)
        if not norm.startswith("/"):
            norm = "/" + norm
        for prefix in self.exclude_paths:
            if prefix and (
                    path == prefix or path.startswith(prefix + "/")
                    or norm == prefix or norm.startswith(prefix + "/")):
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
