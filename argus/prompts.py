"""Operator-prompt builder: a target plus a mode becomes `cfg.goal`.

The web dashboard collects a URL or IP and a MODE and has to turn them into
the one string the agent reads as its instructions - `cfg.goal`, which
`system.build_seed` emits as "Operator goal for this run: ...". This module is
the only place that text is composed, so the difference between the two modes
is in one file instead of in a form handler.

The two modes are not two wordings of the same prompt:

  lab         a CTF challenge or a deliberately vulnerable practice app the
              operator owns. Permissive - find bugs, exploit them, write a
              PoC. No authorization record, because no third party's system
              is involved.

  engagement  a real system the operator says they are authorized to test.
              An Authorization record naming who authorised it, the scope and
              the window is REQUIRED; without a complete one `build_prompt`
              refuses. The prompt it builds is bounded: prove the
              vulnerability and stop.

What this module can and cannot check, stated rather than implied: it checks
the SHAPE of what it was handed - a known mode, a target that could be a
URL/host/IP, an Authorization whose required fields are filled. It can also
ask the OPERATOR'S `ScopeGuard` whether the target is in scope, but only when
the caller passes one (`scope=`); without it this module returns no scope
verdict at all. It used to construct a guard from the very URL it then
checked, which measurably could not refuse anything - `allowed_hosts` was
`{that host}` and `allow_private` was forced True for a private target, so
`http://169.254.169.254/latest/meta-data/` validated clean while the comment
above the call claimed the guard was the authority. The authority on scope is
the guard built from the operator's config and enforced on every request in
`httpclient.GuardedClient.send`; a prompt builder is not a second one.

It cannot check that the operator owns the lab, that the named person exists,
that they authorised anything, or that the window is now. No local check can
establish any of that, and a function that implied otherwise would be worse
than one that says so: the record is carried into the prompt and into the
session's `meta.json` as the operator's declaration, which is the audit
trail, not a verification.

One consequence of that persistence drives two refusals below: everything in
this prompt is written to `meta.json` (`loop.py` and `team/coordinator.py`
both store `goal` in the session meta), and the secret-redaction gate only
redacts values the operator declared with `--secret`. A password typed into
the dashboard's URL field as `http://user:pass@host/` is not a declared
secret, so it would persist verbatim into an artifact. Userinfo in the target
is therefore refused here, not stripped - stripping would silently change
which URL the agent was told to test. And because a refusal goes to the
dashboard and its log, every reason that echoes the target is redacted at the
point of writing it (`_safe`, `_safe_exc`) rather than relying on the
credential check running first - it does not: three earlier checks fire
before it, and one of them was measured returning the password.
"""
from __future__ import annotations

import ipaddress
import re
import textwrap
import urllib.parse
from collections.abc import Mapping
from dataclasses import dataclass, fields

from .scope import ScopeError, ScopeGuard

MODES = ("lab", "engagement")

# Bounds on operator free text. Refused rather than truncated: this text is
# the agent's instructions, and silently dropping half of an operator's
# sentence is the one failure mode a prompt builder must not have.
MAX_EXTRA = 2000
MAX_FINDINGS_DIR = 300
MAX_FIELD = 400

# What a complete engagement authorization has to name. `reference` (contract
# or ticket id) is deliberately not here: plenty of real authorizations are an
# email, and inventing a required ticket number would push operators into
# typing a fake one, which is worse than not having it.
REQUIRED_AUTH_FIELDS = ("authorised_by", "scope", "window")


class PromptRefused(ValueError):
    """A refusal carrying its reasons as a LIST, not only as one string.

    `preview` used to rebuild the list by splitting `str(exc)` on "; ", the
    same separator `build_prompt` joins with - a lossy round-trip over
    operator-controlled text. Measured: an authorization window of
    "ASAP; today" reached the dashboard as two bullets, the first a truncated
    misquote of what the operator typed ("...names no date or time ('ASAP"),
    and a target of "http://127.0.0.1:8080/a; b" the same way. The joined
    message is kept, and `ValueError` is kept as the base class, so every
    existing caller's `except ValueError` and the one-line message are
    unchanged.
    """

    def __init__(self, reasons):
        if isinstance(reasons, str):
            reasons = [reasons]
        self.reasons = [str(r).strip() for r in reasons if str(r).strip()]
        super().__init__("; ".join(self.reasons))


def _flatten(value: str, limit: int = MAX_FIELD) -> str:
    """One line, no control characters, bounded length.

    The authorization record is emitted as `name: value` lines and the whole
    prompt is the agent's instructions, so a value carrying a newline could
    forge a line the operator never wrote - `window="7 Jan\\nscope: all of
    prod"` would read exactly like a scope the record does not grant. The
    value is kept otherwise verbatim; only the framing characters go.
    """
    text = "".join(" " if ch < " " or ch == "\x7f" else ch
                   for ch in str(value))
    text = " ".join(text.split())
    return text[:limit]


@dataclass(frozen=True)
class Authorization:
    """The operator's declaration that this engagement is authorized.

    Frozen because it is carried verbatim into the prompt and the session
    meta: the record the agent was run under must not be mutable by anything
    downstream of the decision to run.
    """

    authorised_by: str = ""
    scope: str = ""
    window: str = ""
    reference: str = ""      # contract or ticket id, optional

    def missing(self) -> list[str]:
        """Required fields left empty, in field order.

        Whitespace-only counts as empty: a form that submits " " has not
        named anyone. Returned as field names so the caller can light up the
        right input rather than parse a sentence.
        """
        return [name for name in REQUIRED_AUTH_FIELDS
                if not _flatten(getattr(self, name, "")).strip()]

    def is_empty(self) -> bool:
        """Nothing filled in at all - no record rather than a partial one."""
        return not any(_flatten(getattr(self, f.name, "")).strip()
                       for f in fields(self))

    def lines(self) -> list[str]:
        """The record as the prompt shows it: flattened, in field order."""
        out = []
        for f in fields(self):
            value = _flatten(getattr(self, f.name, ""))
            if value:
                out.append(f"  {f.name.replace('_', ' ')}: {value}")
        return out


# A dashboard POST arrives as JSON, and the field may be spelled either way
# round. Accepting both spellings is not politeness: `authorized_by` silently
# ignored would mean a filled-in form refused as incomplete, naming a field
# the operator can see they filled in.
_AUTH_ALIASES = {
    "authorised_by": "authorised_by",
    "authorized_by": "authorised_by",
    "scope": "scope",
    "window": "window",
    "reference": "reference",
}


def _as_auth(auth) -> Authorization | None:
    """Coerce what the HTTP layer has to an Authorization, or None if it is
    not a record at all (the caller turns that into a refusal reason)."""
    if auth is None:
        return Authorization()
    if isinstance(auth, Authorization):
        return auth
    if isinstance(auth, Mapping):
        seen: dict[str, dict[str, str]] = {}
        for key, value in auth.items():
            name = str(key).strip().lower()
            field_name = _AUTH_ALIASES.get(name)
            if field_name and value is not None:
                seen.setdefault(field_name, {})[name] = str(value)
        kwargs: dict[str, str] = {}
        for field_name, spellings in seen.items():
            # Exact field name wins over an alias. Both spellings present
            # with different values used to resolve by mapping order, which
            # is no way to decide who authorised the engagement.
            kwargs[field_name] = spellings.get(
                field_name, next(iter(spellings.values())))
        return Authorization(**kwargs)
    return None


_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
# `host:port` is indistinguishable from `scheme:path` by RFC 3986 grammar
# alone, and the dashboard's target box will get `localhost:8080` typed into
# it all day. Fixing the scheme detection above introduced this: with
# `_SCHEME_RE` alone, `localhost:8080` parsed as the scheme `localhost` and
# was refused with a message about schemes. A colon followed by digits and
# then nothing but a path/query/fragment is a port.
_HOST_PORT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:\d+(?:[/?#]|$)")


def _normalise_target(target) -> str:
    """The target as a URL, or "" when it cannot be one.

    A bare host or IP gets `http://`, which is what `ScopeGuard` does with
    its own target argument - the two must agree about what `example.com`
    means or the guard would check a different URL than the prompt names.
    A string that already carries ANY scheme is left alone, so the scheme
    check in `_target_reasons` sees what the operator actually typed.
    """
    if not isinstance(target, str):
        return ""
    text = target.strip()
    if not text:
        return ""
    has_scheme = (_SCHEME_RE.match(text)
                  and not _HOST_PORT_RE.match(text))
    return text if has_scheme else "http://" + text


def _host_plausible(host: str) -> bool:
    """Could this be a hostname or an IP literal?

    Syntax only. A single-label host (`localhost`, `intranet`) is accepted:
    labs run on loopback and internal engagements really do name one-label
    hosts, so requiring a dot would refuse real work to catch a typo. Whether
    the host EXISTS is not checked here and is not checkable without asking a
    resolver what the operator already knows.
    """
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    host = host.rstrip(".")
    if not host or len(host) > 253:
        return False
    for label in host.split("."):
        if not 1 <= len(label) <= 63:
            return False
        if label.startswith("-") or label.endswith("-"):
            return False
        if not all(ch.isascii() and (ch.isalnum() or ch == "-")
                   for ch in label):
            return False
    return True


# Userinfo in the authority, with or without the "//" - a bare
# `admin:pw@host` typed into the dashboard has no slashes.
_USERINFO_RE = re.compile(r"(^|//)[^/@]*@")


def _safe(raw: str) -> str:
    """The operator's target as a refusal message may repeat it.

    Credential values never reach an artifact in this repo, and a refusal
    goes to the dashboard and its log. Two reasons below echo the text as
    typed, and `http://u:pw@h /x` trips the WHITESPACE check before the
    credentials check ever runs - so the echo has to be safe by itself
    rather than safe because of the order of the checks.
    """
    return _USERINFO_RE.sub(lambda m: m.group(1) + "<redacted>@", raw)


def _userinfo_parts(raw: str) -> list[str]:
    """The exact credential bytes the operator typed, if any.

    Returned as the userinfo as a whole plus each colon-separated half, which
    is what must not survive in any message this module echoes.
    """
    parts: list[str] = []
    for m in _USERINFO_RE.finditer(raw):
        creds = m.group(0)[len(m.group(1)):-1]
        if creds:
            parts.append(creds)
            parts += [half for half in creds.split(":") if half]
    return parts


def _safe_exc(exc: BaseException, raw: str) -> str:
    """An exception message that may have interpolated the target, redacted.

    MEASURED LEAK, which is why this exists rather than `_safe(str(exc))`:
    `urlparse("http://admin:hunter2@ex\u2100ample.com/")` raises from
    urllib's `_checknetloc` with the ORIGINAL netloc in the message, and that
    message was interpolated into "target is not a URL (...)" and returned to
    the dashboard's HTTP JSON with the password in it. Any non-ASCII
    character whose NFKC form contains / ? # @ or : triggers it (U+2100 is
    "a/c"). That check fires BEFORE the credential check, so the module's own
    invariant - an echo is safe by itself, not safe because of the order of
    the checks - was false on this path.

    The credential is removed by name rather than by re-matching the message:
    the wording belongs to urllib and can put the userinfo anywhere in it,
    and `_safe`'s regex is anchored for a target string, not for prose. If
    any piece of the userinfo still survives the substitution the message is
    dropped whole - which also drops a legitimate message when the username
    happens to appear in the host, and a less informative refusal is the
    right error to prefer here.
    """
    text = str(exc)
    parts = _userinfo_parts(raw)
    if not parts:
        return text
    for creds in parts:
        text = text.replace(creds, "<redacted>")
    if any(creds in text for creds in parts):
        return "message withheld: it repeated the credential in the target"
    return text


def _as_guard(scope):
    """The operator's scope as something that can refuse a URL.

    Returns (guard, reasons). `(None, [])` means no scope was supplied, and
    `_target_reasons` then reports no scope verdict rather than manufacturing
    one. Accepted: anything with a `.check(url)` method - the operator's own
    `ScopeGuard`, used as-is so no new DNS lookup is paid here - or a mapping
    of `ScopeGuard`'s arguments, which must name its own `target`.

    A mapping with no `target` is a refusal, not an empty check: building the
    guard from the URL under test is exactly the defect this parameter
    replaces, because `ScopeGuard.__init__` makes that URL's host the whole
    allowlist and forces `allow_private` on for a private one.
    """
    if scope is None:
        return None, []
    if callable(getattr(scope, "check", None)):
        return scope, []
    if isinstance(scope, Mapping):
        target = str(scope.get("target") or "").strip()
        if not target:
            return None, ["scope names no target - give the scope's own "
                          "target, so the guard is not built from the URL "
                          "it is judging"]
        try:
            guard = ScopeGuard(
                target,
                extra_hosts=[str(h) for h in (scope.get("extra_hosts") or [])],
                exclude_paths=[str(x) for x in
                               (scope.get("exclude_paths") or [])],
                allow_private=bool(scope.get("allow_private", False)),
                include_subdomains=bool(
                    scope.get("include_subdomains", True)),
            )
        except (ScopeError, OSError, ValueError, TypeError) as exc:
            return None, [f"scope could not be built ({exc})"]
        return guard, []
    return None, ["scope must be a ScopeGuard or a mapping of its fields, "
                  f"got {type(scope).__name__}"]


def _target_reasons(target, scope=None) -> list[str]:
    """Why this target cannot be put in a prompt. Empty list means it can."""
    if not isinstance(target, str) or not target.strip():
        return ["target is empty - give a URL, hostname or IP"]
    raw = target.strip()
    if any(ch < " " or ch == "\x7f" for ch in raw):
        return ["target contains control characters"]
    if any(ch.isspace() for ch in raw):
        return [f"target contains whitespace: {_safe(raw)!r}"]
    url = _normalise_target(raw)
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError as exc:
        # `_safe_exc`, not `{exc}`: this message carried the operator's
        # password to the dashboard. See `_safe_exc`. The three echoes below
        # get the same treatment - measured, urllib's port and host
        # exceptions do not repeat the userinfo today, but the invariant is
        # that the echo is safe by itself, not that the wording stays put.
        return [f"target is not a URL ({_safe_exc(exc, raw)})"]
    if parsed.scheme.lower() not in ("http", "https"):
        hint = ("" if "/" in raw else
                " (if you meant a host and port, write host:<digits>)")
        return [f"target scheme {parsed.scheme or '(none)'!r} is not "
                f"http or https{hint}"]
    try:
        parsed.port
    except ValueError as exc:
        # `urlparse` parses lazily: `.port` is where `:99999999` and `:abc`
        # raise. Nothing here accessed it, so an unusable port reached the
        # prompt and failed much later, inside the client.
        return [f"target port is not usable ({_safe_exc(exc, raw)})"]
    try:
        host = parsed.hostname
    except ValueError as exc:
        return [f"target has no usable host ({_safe_exc(exc, raw)})"]
    if not host:
        return [f"target names no host: {_safe(raw)!r}"]
    if parsed.username or parsed.password or "@" in parsed.netloc:
        # See the module docstring: the prompt is persisted to meta.json and
        # only --secret values are redacted there, so a credential in the URL
        # would be written to an artifact by this function.
        return ["target carries credentials in the URL (user:pass@host) - "
                "pass them with --header/--secret instead, so they are not "
                "written into the prompt and the session meta"]
    if not _host_plausible(host):
        return [f"target host is not a hostname or IP: {host!r}"]
    # The scope verdict comes from the OPERATOR'S guard or not at all.
    #
    # What was here built `ScopeGuard(url)` from the very URL it then
    # checked, so every branch of `check()` was unreachable: the host was the
    # whole allowlist, `allow_private` was forced True for a private target
    # (scope.py:206), `exclude_paths` was empty, and the scheme and host were
    # already settled above. Measured with a spy on `check()`:
    # `validate("lab", t) == []` for every t in
    # http://169.254.169.254/latest/meta-data/, http://10.0.0.1/,
    # http://192.168.1.1/admin, http://224.0.0.1/ and http://[::1]/ - the
    # cloud-metadata address included - with `allow_private` True on all of
    # them. A verdict that cannot come out the other way is not a check.
    #
    # It was not free, either: `ScopeGuard.__init__` resolves the host and
    # caches it PER INSTANCE, and a fresh instance was built per call, so
    # every preview of a hostname target paid one `getaddrinfo`. Measured
    # against a non-answering resolver: 5 previews took 10.01s wall (2s each,
    # scope._RESOLVE_DEADLINE_S) and left 5 daemon threads abandoned inside
    # `getaddrinfo` (scope.py:58-61), living on until the resolver gives up
    # (~24s). `POST /api/prompt` calls this per request and is not bounded by
    # MAX_CONCURRENT_RUNS, which covers runs and not previews.
    guard, scope_reasons = _as_guard(scope)
    if scope_reasons:
        return scope_reasons
    if guard is None:
        return []
    try:
        guard.check(url)
    except ScopeError as exc:
        return [f"scope guard refuses this target: {_safe_exc(exc, raw)}"]
    except (OSError, ValueError) as exc:
        return [f"target could not be checked against scope "
                f"({_safe_exc(exc, raw)})"]
    return []


def validate(mode, target, auth=None, *, scope=None, findings_dir="",
             extra="") -> list[str]:
    """Human-readable refusal reasons; an empty list means OK.

    Checked: the mode is one of MODES; the target could be a URL/host/IP, and
    when `scope` names the operator's own `ScopeGuard` (or a mapping of its
    arguments, including its own target) that guard admits it; in engagement
    mode the Authorization is complete; and the two free-text fields are
    within their bounds. NOT checked, because no local check can establish
    it: that the operator owns the target, that the named authoriser exists
    or agreed, that the scope line matches a contract, or that the window is
    open now. A complete record is a declaration on the record, not a
    verification. Without `scope` there is no scope verdict here at all - see
    the module docstring for the guard this module used to build and why it
    could not refuse anything.

    `findings_dir` and `extra` are keywords here so that "an empty list means
    OK" is true of the call `build_prompt` makes. Their bounds used to live
    only in `build_prompt`, so `validate(...) == []` could be followed by
    `build_prompt(...)` raising on the same inputs.
    """
    reasons: list[str] = []
    mode_name = mode if isinstance(mode, str) else ""
    if mode_name not in MODES:
        shown = mode if isinstance(mode, str) else type(mode).__name__
        reasons.append(f"unknown mode {shown!r} - modes are: "
                       + ", ".join(MODES))
    reasons += _target_reasons(target, scope)

    record = _as_auth(auth)
    if record is None:
        reasons.append("authorization must be an Authorization or a mapping "
                       f"of its fields, got {type(auth).__name__}")
        return reasons

    for f in fields(record):
        value = getattr(record, f.name, "")
        # Coerced rather than `isinstance(value, str)`: an Authorization
        # built in Python (cli.py, the team plane) can carry a non-string,
        # and the guard used to skip it entirely while `_flatten` silently
        # truncated an over-long one to MAX_FIELD on the way into the prompt
        # - the one thing this bound exists to refuse.
        value = value if isinstance(value, str) else str(value)
        if len(value) > MAX_FIELD:
            reasons.append(
                f"authorization field {f.name!r} is {len(value)} characters; "
                f"the limit is {MAX_FIELD} - refused rather than truncated, "
                "because the record is the audit trail")

    if mode_name == "engagement":
        gaps = record.missing()
        if gaps:
            reasons.append(
                "engagement mode needs an authorization record; missing: "
                + ", ".join(gaps))
            # Each field named on its own line too, so a form can mark the
            # inputs without parsing the sentence above.
            reasons += [f"authorization field {name!r} is empty"
                        for name in gaps]
        elif not any(ch.isdigit() for ch in _flatten(record.window)):
            # The only locally checkable thing about a window: a time window
            # names a date or a time. "whenever" and "ASAP" are not windows.
            # This says nothing about whether the window is open now.
            reasons.append(
                "authorization field 'window' names no date or time "
                f"({record.window!r}) - give the window the authorisation "
                "covers, e.g. '2026-11-18 09:00 to 2026-11-22 18:00 UTC'")
    # Measured defect: `for ch in record.window` raised TypeError out of a
    # function documented to RETURN reasons when the field was an int.
    # `_flatten` above coerces with `str()`, as every other reader of the
    # record already did; `preview` masked this behind its catch-all, so only
    # a direct caller - cli.py, the team plane - ever saw the exception.
    reasons += _text_reasons(extra, findings_dir)
    return reasons


def _text_reasons(extra, findings_dir) -> list[str]:
    """Bounds on the two free-text fields that are not the target."""
    reasons = []
    if not isinstance(extra, str):
        reasons.append(f"extra must be text, got {type(extra).__name__}")
    elif len(extra) > MAX_EXTRA:
        reasons.append(f"extra is {len(extra)} characters; the limit is "
                       f"{MAX_EXTRA} (refused rather than truncated, so no "
                       "instruction is silently dropped)")
    if not isinstance(findings_dir, str):
        reasons.append("findings_dir must be text, got "
                       f"{type(findings_dir).__name__}")
    else:
        if len(findings_dir) > MAX_FINDINGS_DIR:
            reasons.append(f"findings_dir is {len(findings_dir)} characters; "
                           f"the limit is {MAX_FINDINGS_DIR}")
        if any(ch < " " or ch == "\x7f" for ch in findings_dir):
            reasons.append("findings_dir contains control characters")
    return reasons


_LAB_HEAD = """\
You are an expert in web application security. The target below is one the
operator owns - a CTF challenge or a deliberately vulnerable practice app.
Carry out reconnaissance, find the vulnerabilities, exploit the ones you find,
and write up a PoC for each.

Target: {target}"""

_LAB_BODY = """\
Recon first: fingerprint, then crawl and js_recon, then wordlist_fuzz for what
nothing linked to. run_external gives you nmap, ffuf, nuclei, sqlmap and curl.
Then name a hypothesis per input and drive the probe_* tool for the class you
suspect; load_skill carries the methodology for a class, and next_action tells
you what the recorded evidence says to do next.

Read `argus proof <class>` BEFORE probing a class, so you collect what it asks
for on the first pass: rce is the output of `id; echo <nonce>` with the nonce
tying it to your probe, sqli is the DBMS fingerprint plus one row from a named
table. Quote the bytes the target returned, verbatim - a summary does not
grade. Denial of service is refused by the proof matrix, so do not try to
prove availability impact.

{closing}"""

_ENGAGEMENT_HEAD = """\
You are an expert in web application security, testing a system the operator
states they are authorized to test. The record below is the whole of your
permission. It is the operator's declaration, carried here verbatim; nothing
in this tool verified it."""

_ENGAGEMENT_BOUNDS = """\
Bounds. These are the task, not a disclaimer:

- Prove each vulnerability, then stop. `argus proof <class>` prints what the
  class must produce; collect exactly that and nothing further.
- rce stops at the output of `id; echo <nonce>`. No shell, no second command,
  no file written, no outbound connection from the target.
- sqli stops at the DBMS fingerprint plus one row from a named table. Do not
  dump the table, walk the schema past it, or read a credential column.
- Read no data beyond what proves the read. One record proves an IDOR; the
  other ten thousand are someone's personal data and are not evidence.
- No persistence, no backdoor, no added account, no lateral movement to a
  second host, no denial of service - the proof matrix refuses availability
  impact by construction, because its proof is the damage.
- The scope line above bounds the hosts. If a finding points at something
  outside it, record the pointer and stop; do not follow it. The scope guard
  refuses out-of-scope requests and a refusal is a decision: read it and
  change the request, never retry it verbatim.
- Credential values never go into a finding, a note or a report - name where
  the credential was found and what it opened, not the value.
- If the work would run outside the window above, stop and report instead.
- Invent nothing. No endpoint, parameter, version, CVE or number that was not
  observed in this engagement's own evidence."""


def _findings_clause(findings_dir: str) -> str:
    """Where the PoC goes, as one unwrapped sentence fragment.

    Empty `findings_dir` is not an error: the session directory already holds
    findings.json, report.md and notes.md, so the honest instruction is to
    use them rather than to name a path nobody set.

    Unwrapped because the caller fills the paragraph it lands in - the first
    version carried its own newlines and produced a 90-column line in the
    middle of a hand-wrapped block whenever a path was supplied.
    """
    clean = _flatten(findings_dir, MAX_FINDINGS_DIR)
    if clean:
        return ("and save each PoC - the request, the response excerpt and "
                f"the steps to reproduce - into {clean}")
    return ("and put the reproduction steps in notes.md with `note`, where "
            "the report renderer picks them up")


def build_prompt(mode, target, *, auth=None, findings_dir="",
                 extra="", scope=None) -> str:
    """The operator prompt for `cfg.goal`.

    Raises PromptRefused (a ValueError) listing EVERY reason when the request
    is refused - one reason at a time would make a dashboard user fix a form
    field by field, and the reasons are carried as a list so nothing has to
    re-parse the message.
    """
    reasons = validate(mode, target, auth, scope=scope)
    # Checked here as well as inside `validate`, deduplicated, for the same
    # reason the engagement-record gate below is duplicated: one gate in one
    # place is one edit away from none. `validate` is monkeypatched out in
    # two of this module's own tests precisely to prove that.
    reasons += [r for r in _text_reasons(extra, findings_dir)
                if r not in reasons]
    if reasons:
        raise PromptRefused(reasons)

    record = _as_auth(auth) or Authorization()
    url = _normalise_target(target)
    note = _flatten(extra, MAX_EXTRA)

    if mode == "lab":
        parts = [_LAB_HEAD.format(target=url)]
        # A record is not required here and an incomplete one is dropped
        # rather than printed: a half-filled block reads like a complete
        # authorization. A complete one is carried, because discarding an
        # authorization the operator took the trouble to type is the wrong
        # direction even when the mode does not need it.
        if not record.is_empty() and not record.missing():
            parts.append("Operator-supplied authorization record (verbatim):\n"
                         + "\n".join(record.lines()))
        parts.append(_LAB_BODY.format(closing=textwrap.fill(
            "Record every bug with record_finding (class, endpoint, verbatim "
            "excerpt) so it lands in findings.json with a proof grade, "
            + _findings_clause(findings_dir)
            + ". Call finish() when the target is exhausted or the budget "
            "is.", width=78, break_long_words=False,
            break_on_hyphens=False)))
        if note:
            parts.append(f"Operator notes: {note}")
        return "\n\n".join(parts)

    if mode != "engagement":
        raise PromptRefused(f"unknown mode {mode!r} - modes are: "
                            + ", ".join(MODES))
    gaps = record.missing()
    if gaps:
        # Unreachable through validate() above, and deliberately duplicated:
        # an engagement prompt with an empty authorization block is the one
        # output of this module that must never exist, so it is refused at
        # the point of writing it as well as at the point of validating.
        raise PromptRefused("engagement mode needs an authorization record; "
                            "missing: " + ", ".join(gaps))

    parts = [_ENGAGEMENT_HEAD,
             "AUTHORIZATION RECORD (verbatim, as the operator entered it):\n"
             + "\n".join(record.lines()),
             f"Target: {url}"]
    # Operator notes go ABOVE the bounds, deliberately. The bounds are what
    # the authorization allows; text appended after them would have the last
    # word in the prompt, and a free-text field on a web form is not where
    # the limits of an engagement get rewritten.
    if note:
        parts.append(f"Operator notes: {note}")
    parts.append(_ENGAGEMENT_BOUNDS)
    parts.append(textwrap.fill(
        "Work the ladder: recon (fingerprint, crawl, js_recon), map the "
        "inputs, name a hypothesis, drive the probe_* tool for it, verify "
        "it, and record it with record_finding and its verbatim excerpt, "
        + _findings_clause(findings_dir)
        + ". Call finish() when the scope is covered or the budget is "
        "spent.", width=78, break_long_words=False,
        break_on_hyphens=False))
    return "\n\n".join(parts)


# `break_long_words=False, break_on_hyphens=False` on both fills above, and
# why: with textwrap's defaults the findings_dir was broken ACROSS A LINE, so
# the agent was told to write PoCs into a path that does not exist. Measured,
# engagement mode with findings_dir="/srv/pt/acme-2026-external-webapp-
# findings" emitted "... into /srv/pt/acme-2026-external-\nwebapp-findings."
# - 42 characters split at a hyphen, and `findings_dir in text` False. Lab
# mode broke the same way for any path over ~110 characters. The path is now
# never split; a path long enough to need its own line overruns the 78-column
# wrap, which is the right trade - a wrapped path is not a path, and
# MAX_FINDINGS_DIR already bounds how far it can overrun.


def preview(mode, target, **kw) -> dict:
    """{"ok", "prompt", "errors"} - never raises.

    This is what the HTTP layer calls on every form submission, so garbage in
    any argument has to come back as an error list, not a 500. Unknown
    keyword arguments are ignored: a dashboard that grows a field must not be
    able to take the preview endpoint down before this module knows about it.
    """
    try:
        kwargs = {name: kw[name] for name in
                  ("auth", "findings_dir", "extra", "scope") if name in kw}
        prompt = build_prompt(mode, target, **kwargs)
        return {"ok": True, "prompt": prompt, "errors": []}
    except ValueError as exc:
        # The reasons as a LIST, from the exception, instead of splitting the
        # joined message on "; ". That split was a lossy round-trip over
        # operator text: window="ASAP; today" reached the dashboard as
        # ["...names no date or time ('ASAP", "today') - give the window..."]
        # - two bullets, the first a truncated misquote. A plain ValueError
        # from somewhere unforeseen is one reason, not several, because
        # nothing here knows how it was composed.
        reasons = getattr(exc, "reasons", None)
        if reasons is None:
            reasons = [str(exc)]
        errors = [str(part).strip() for part in reasons if str(part).strip()]
        # A refusal with no reason would reach the dashboard as a refusal
        # with nothing to show the operator, and `web.api.preview_prompt`
        # forces `ok` false on a non-empty error list - so an empty one here
        # is the shape that could display a refusal and a prompt at once.
        return {"ok": False, "prompt": "",
                "errors": errors or ["prompt refused and gave no reason - "
                                     "this is a bug in argus.prompts"]}
    except Exception as exc:  # noqa: BLE001 - see the docstring: no 500s
        # Anything unforeseen is reported as a refusal naming its type. A
        # bare `except ValueError` was the first version of this and it let a
        # TypeError from a non-string mode through to the caller.
        return {"ok": False, "prompt": "",
                "errors": [f"could not build a prompt: "
                           f"{type(exc).__name__}: {str(exc)[:200]}"]}
