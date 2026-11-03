"""session — the identities an engagement can act as, and requests issued as one.

The authenticated half of an engagement was the part a model had to remember.
`http.probe` takes a cookie string, so every authenticated request restated the
credential, every authorization comparison was assembled by hand from two
separate calls, and the field the differential verifier actually reads —
`actor` — was optional. A model that forgot it produced a cross-read that could
not be graded, which is indistinguishable from not having probed at all.

These six tools move that into the ledger:

* `session.add` records an identity you already hold; `session.login` obtains
  one by replaying a login request; `session.refresh` replays it again.
* `session.list` shows the identities **described, never valued**.
* `session.probe_as` issues one request as a named identity and writes `actor`
  into the evidence record itself, so it cannot be forgotten.
* `session.compare_as` issues the same request as two identities and as
  `unauthenticated`, takes the actor's own-resource control, and grades the set
  against the `idor` requirement in one call.

Two refusals are worth stating in advance.

`session.login` stores nothing when its `success` marker is absent from the
response. A login that silently failed is worse than no identity at all: every
later probe then runs as an anonymous caller while the ledger says it ran as
`alice`, and the resulting "authorization finding" is an unauthenticated 200
with a label on it.

No credential these tools send or collect is written verbatim into an evidence
record. The store is the only file that holds a value
(`argus/ledger/identities.py` says why), so these tools strip the material out
of the request they just sent before handing it to the ledger — and, on a login
or a refresh, out of the response too, because that response carries the
credential by construction. `httpkit.HttpResponse.to_evidence()` keeps request
headers verbatim, and `argus.util.redact` knows credential *shapes*, not an
opaque session cookie, so neither of them would have done it. What replaces the
value is `<credential:alice>`, not a blank: a reviewer needs to see that the
request carried alice's credential, and the `actor` field plus
`extracted.identity` says which credential it was.

Where that stops, and why: a *probe* response body is not scrubbed. The body is
the observation, and on the fixture scrubbing it would have replaced the note's
`owner` field and the proof with it. So a session cookie echoed back into a
response body does reach the ledger. That is a `secret-exposure` finding in its
own right, and nothing here detects it.

What these tools will not do: they do not guess, spray, reuse or escalate a
credential, and there is no tool here that takes a password list. An identity is
one the operator supplied or one a login endpoint returned when given the
operator's own credentials.
"""
from __future__ import annotations

import email.utils
import json as jsonlib
import re
import urllib.parse

from ... import config
from ...ledger import identities as identity_mod
from ...ledger import proof as matrix
from ...ledger.state import RECON
from ...util import now_iso
from .. import httpkit
from ..mcp import Server, ToolContext

SERVER = Server("session", "identities, login, and requests issued as a named identity")

_SCHEME_HELP = ("cookie | bearer | basic | header | query | none. `query` is for an application "
                "that takes the caller's name in a query parameter and trusts it — not an "
                "authentication scheme, which is usually the point. `none` belongs to the reserved "
                "`unauthenticated` control and is refused for any other name: a named identity "
                "carrying no credential would put its name on an anonymous request")

_IDENTITY_FIELDS = {
    "field": {"type": "string",
              "description": "the cookie name, header name or query parameter that carries the "
                             "credential (default Authorization for bearer/basic, session for cookie)"},
    "note": {"type": "string", "description": "where this identity came from, in one line"},
    "entitled_to": {"type": "array",
                    "description": "subject names this identity is allowed to reach, free text"},
    "not_entitled_to": {"type": "array",
                        "description": "subject names it must NOT reach. This is what lets an "
                                       "authorization proof say why the actor should have failed"},
}

_REQUEST_FIELDS = {
    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]},
    "params": {"type": "object", "description": "query parameters merged into the URL"},
    "headers": {"type": "object",
                "description": "extra headers. A header that would overwrite the credential the "
                               "named identity supplies — Cookie, Authorization, its own header — "
                               "is refused rather than applied: the record would say the identity "
                               "made a request somebody else made. Change the identity instead"},
    "body": {"type": "string", "description": "raw request body"},
    "json_body": {"type": "object", "description": "body sent as application/json"},
    "note": {"type": "string", "description": "why this request was issued"},
    "timeout": {"type": "integer", "description": "seconds, default 15"},
}

# Attribute names that appear in a Set-Cookie header and are never the cookie.
_COOKIE_ATTRIBUTES = {"path", "domain", "expires", "max-age", "secure", "httponly",
                      "samesite", "version", "comment", "priority", "partitioned"}

# Below this length a string in a login response is a username or a status word
# as often as it is a token, and withholding it costs the reviewer the body.
TOKEN_FLOOR = 12


# --- plumbing ----------------------------------------------------------------

def _store(context: ToolContext):
    return identity_mod.IdentityStore.load(context.engagement)


def _no_engagement() -> dict:
    return {"ok": False, "error": "no-engagement",
            "message": "the identity store lives in the engagement directory: pass "
                       "engagement=<name>, or set ARGUS_ENGAGEMENT"}


def _unknown(name: str, store) -> dict:
    return {"ok": False, "error": "unknown-identity",
            "message": f"no identity {name!r}; have {store.names()}. Record one with session.add "
                       f"if you already hold the credential, or obtain one with session.login.",
            "next": "session.list shows what this engagement can act as"}


def _reserved_headers(identity) -> set[str]:
    """The header names this identity supplies itself, lowercased.

    `Cookie` counts even though the cookie is passed to `httpkit.request` as
    `cookies=`: that function sets the Cookie header first and then applies
    `headers` over the top, so a caller-supplied `Cookie` replaces the
    identity's own and the merge in `_issue` never sees the collision.
    """
    kwargs = identity.request_kwargs()
    names = {str(name).lower() for name in (kwargs.get("headers") or {})}
    if kwargs.get("cookies"):
        names.add("cookie")
    return names


def _header_conflict(headers: dict | None, *identities) -> dict | None:
    """Refuse a request that overrides the credential of the identity it names.

    Measured, not assumed: `headers={"Cookie": "sid=anything"}` on a cookie
    identity produced an evidence record reading `actor: carol` for a request
    that carried someone else's cookie — the exact record this server exists to
    make impossible — and the substituted value went to disk verbatim, because
    `_scrub` withholds the *stored* identity's material and knows nothing about
    a value that arrived in an argument.
    """
    reserved: set[str] = set()
    for identity in identities:
        if identity is not None:
            reserved |= _reserved_headers(identity)
    clashing = sorted(name for name in (headers or {}) if str(name).lower() in reserved)
    if not clashing:
        return None
    return {"ok": False, "error": "header-conflict",
            "message": f"{clashing} would overwrite the credential the named identity supplies. "
                       f"The request would then be made by someone else while the evidence record "
                       f"said the actor was this identity, which is the one record an authorization "
                       f"proof cannot survive being wrong about.",
            "next": "drop that header, or record what it carries as its own identity with "
                    "session.add and name that identity instead"}


def _claim_query_key(url: str, keys) -> tuple[str, tuple[str, ...]]:
    """Drop the identity's own query parameter from a URL that already carries it.

    `httpkit.request` appends `params` to the existing query rather than
    replacing it, and an application that reads the first occurrence of a
    repeated parameter then answers as whoever the caller's URL named: a probe
    as `alice` against `?id=2&user=admin` was answered `requested_by: admin`
    while the record said `actor: alice`. A URL copied out of a browser carries
    that parameter nearly always, so it is dropped rather than refused, and what
    was dropped is named in the result and in the evidence record.
    """
    split = urllib.parse.urlsplit(url)
    if not split.query:
        return url, ()
    wanted = {str(key) for key in keys}
    existing = urllib.parse.parse_qsl(split.query, keep_blank_values=True)
    kept = [(name, value) for name, value in existing if name not in wanted]
    dropped = tuple(sorted({name for name, _ in existing if name in wanted}))
    if not dropped:
        return url, ()
    return urllib.parse.urlunsplit(split._replace(
        query=urllib.parse.urlencode(kept, quote_via=urllib.parse.quote))), dropped


def _issue(identity, url: str, method: str = "GET", headers: dict | None = None,
           params: dict | None = None, body: str | None = None, json_body: dict | None = None,
           timeout: int = 15) -> tuple[httpkit.HttpResponse, tuple[str, ...]]:
    """One request, with the identity's credential applied by the identity.

    Returns the response and the names of any query parameters the identity took
    over. The identity wins over caller-supplied headers and parameters — a
    caller that could override the auth header while still naming an identity
    would produce a record saying `actor: alice` for a request alice did not
    make — and `_header_conflict` refuses the case the merge cannot win.
    """
    kwargs = identity.request_kwargs()
    own_params = kwargs.get("params") or {}
    taken: tuple[str, ...] = ()
    if own_params:
        url, taken = _claim_query_key(url, own_params)
    merged_headers = {**(headers or {}), **(kwargs.get("headers") or {})}
    merged_params = {**(params or {}), **own_params}
    # Four requests can hang off one compare_as, so the per-request wait is
    # bounded here rather than left to whatever a model types.
    timeout = max(1, min(int(timeout or 15), 120))
    return httpkit.request(method or "GET", url, headers=merged_headers or None,
                           params=merged_params or None, data=body or None, json_body=json_body,
                           cookies=kwargs.get("cookies"), timeout=timeout), taken


def _withhold(blob, pairs: list[tuple[str, str]]):
    if isinstance(blob, str):
        for value, placeholder in pairs:
            if value:
                blob = blob.replace(value, placeholder)
        return blob
    if isinstance(blob, dict):
        return {key: _withhold(value, pairs) for key, value in blob.items()}
    if isinstance(blob, list):
        return [_withhold(item, pairs) for item in blob]
    return blob


def _scrub(record: dict, *identities) -> dict:
    """Withhold credential material from the request side of an evidence record.

    The request subtree, the response headers and the final URL are scrubbed,
    because that is where a credential we sent comes back. `response.body_span`
    is left alone: the body is the observation, and scrubbing it would destroy
    the evidence — on the fixture, where the identity is the string `alice` in a
    query parameter, scrubbing the body would replace the note's `owner` field
    with a placeholder and the proof with it. A credential echoed into a response
    body is a `secret-exposure` finding in its own right, and that is the class
    that should record it.
    """
    pairs = [(material, f"<credential:{identity.name}>")
             for identity in identities if identity is not None
             for material in identity.material()]
    if not pairs:
        return record
    for key in ("target", "payload", "url"):
        if isinstance(record.get(key), str):
            record[key] = _withhold(record[key], pairs)
    if isinstance(record.get("request"), dict):
        record["request"] = _withhold(record["request"], pairs)
    response = record.get("response")
    if isinstance(response, dict):
        for key in ("headers", "final_url"):
            if key in response:
                response[key] = _withhold(response[key], pairs)
    return record


def _record(identity, response: httpkit.HttpResponse, tool: str, *, kind: str = "probe",
            accessed_subject: str = "", is_control: bool = False, note: str = "",
            extracted: dict | None = None) -> dict:
    record = response.to_evidence()
    record.update({
        "kind": kind,
        "tool": tool,
        "target": response.url,
        # `actor` is written here rather than passed by the caller because it is
        # the field `verify_differential` reads, and an optional field that the
        # proof depends on is a field that goes missing.
        "actor": identity.name,
        "note": note,
    })
    if accessed_subject:
        record["accessed_subject"] = accessed_subject
    if is_control:
        record["is_control"] = True
    record["extracted"] = {"identity": identity.describe(), "credential_withheld": True,
                           **(extracted or {})}
    return _scrub(record, identity)


def _shape(response: httpkit.HttpResponse) -> str:
    return (f"{response.status} {response.length}B {response.time_ms}ms"
            if response.status is not None else f"transport error: {response.error}")


def _materially_different(diff: httpkit.Differential) -> bool:
    """Whether two responses really differ, on httpkit's floors rather than a
    second set invented here.

    A whole-body similarity threshold is the wrong measure for an authorization
    comparison, and this is where it was found out: the fixture echoes the
    caller's own name back in `requested_by`, so alice's copy of admin's note is
    never byte-identical to admin's copy, and a 0.98 floor read a textbook
    cross-read as no result. What matters is whether the difference is bigger
    than the noise floor — the same question `httpkit.compare` already answers.
    """
    return diff.status_changed or (abs(diff.length_delta) >= 24 and diff.body_similarity < 0.98)


# --- recording an identity you already hold ----------------------------------

@SERVER.tool(
    "session.add",
    "Record an identity whose credential you already have: a cookie, a bearer token, basic "
    "credentials, a custom header, or a query parameter an application trusts. The value is written "
    "to the engagement's identity store, 0600, and never appears in evidence, a digest or a report "
    "— session.list shows the shape. Declaring not_entitled_to is what lets a later authorization "
    "proof say why this identity should not have been able to read something.",
    {"properties": {
        "name": {"type": "string", "description": "how probes will refer to it: alice, admin, …"},
        "scheme": {"type": "string", "enum": list(identity_mod.SCHEMES),
                   "description": _SCHEME_HELP},
        "value": {"type": "string",
                  "description": "the credential: the cookie value, the token, or user:password "
                                 "for basic. Required for every scheme but 'none', which only the "
                                 "reserved 'unauthenticated' control may use"},
        **_IDENTITY_FIELDS,
    }, "required": ["name", "scheme"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def add(context: ToolContext, name: str, scheme: str, value: str = "", field: str = "",
        note: str = "", entitled_to: list | None = None,
        not_entitled_to: list | None = None) -> dict:
    if not context.engagement:
        return _no_engagement()
    try:
        identity = identity_mod.Identity(
            name=name, scheme=scheme, field=field, value=value, note=note,
            entitled_to=tuple(entitled_to or ()), not_entitled_to=tuple(not_entitled_to or ()))
        identity_mod.put(context.engagement, identity)
    except ValueError as error:
        return {"ok": False, "error": "bad-identity", "message": str(error),
                "next": "fix the argument the message names and call again"}
    store = _store(context)
    shape = identity.describe()
    return {
        "summary": (f"identity {identity.name!r} recorded: {shape['scheme']}"
                    + (f":{shape['field']}" if shape['field'] else "")
                    + f", {shape['value_length']} chars"
                    + (f" ending {shape['last4']}" if shape['last4'] else "")
                    + f". {len(store.names())} identity(ies) in this engagement."),
        "result": "signal",
        "data": {"identity": shape, "identities": store.names()},
        "output": "\n".join(i.line() for i in store.all()),
        "next": ("probe with it: session.probe_as identity=" + identity.name
                 + ". An authorization class needs two identities and the unauthenticated control"
                 + (" — add the second one now" if len(store.identities) < 2 else
                    "; unauthenticated always exists, so you have what compare_as needs")
                 + ("" if identity.not_entitled_to else
                    ". Nothing is declared in not_entitled_to, so a finding made with this identity "
                    "will have to say the entitlement was assumed")),
    }


@SERVER.tool(
    "session.list",
    "The identities this engagement can act as, described and never valued: name, scheme, which "
    "header or cookie carries the credential, the value's length and last four characters, when it "
    "was obtained, whether it has expired and what it is declared entitled to. There is no tool "
    "that returns a credential value — the store exists so that no model has to hold one.",
    {"properties": {}, "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def list_identities(context: ToolContext) -> dict:
    if not context.engagement:
        return _no_engagement()
    store = _store(context)
    digest = store.digest()
    return {
        "summary": (f"{digest['count']} identity(ies): {', '.join(store.names())}"
                    + (f"; stale: {', '.join(digest['stale'])}" if digest["stale"] else "")),
        "result": "signal" if digest["count"] > 1 else "no-signal",
        "data": digest,
        "output": "\n".join(identity.line() for identity in store.all()),
        "next": ("session.compare_as can grade an authorization class with these"
                 if digest["count"] > 2 else
                 "only the unauthenticated control exists, or one identity plus it. An "
                 "authorization class needs two named identities: session.login or session.add"),
    }


# --- obtaining one -----------------------------------------------------------

def _parse_cookies(header_value: str) -> list[tuple[str, str]]:
    """Cookie name/value pairs out of a Set-Cookie header.

    One header can legally carry several cookies, comma-joined, so scanning for
    `name=value` and skipping the attribute names recovers all of them where a
    naive split on the first `;` recovers one.

    What it cannot recover is a cookie in a *second* Set-Cookie header.
    `httpkit` reads a response's headers into a dict, so repeated headers
    collapse to the last one and the earlier ones are gone before this function
    sees anything. Measured against a login endpoint that sets a session cookie
    and then a CSRF cookie: only the CSRF cookie survived, and
    `capture=set-cookie:sid` correctly reported that no `sid` was there. That
    makes multi-cookie logins a real gap, not a parsing choice — `_capture` says
    so in its refusal rather than leaving a model to retry a correct rule.
    """
    found = []
    for piece in re.split(r"[;,]\s*", header_value or ""):
        if "=" not in piece:
            continue
        name, _, value = piece.partition("=")
        name, value = name.strip(), value.strip().strip('"')
        if not name or name.lower() in _COOKIE_ATTRIBUTES or not value:
            continue
        found.append((name, value))
    return found


def _segment_for(header_value: str, name: str) -> str:
    """The slice of a Set-Cookie header that belongs to one cookie.

    Needed when one header carries several: searching the whole string for
    Max-Age attributes the first cookie's lifetime to whichever cookie was
    captured, which is how an identity gets an expiry it was never given.
    """
    text = header_value or ""
    names = [name_ for name_, _ in _parse_cookies(text)]
    if name not in names:
        return text
    start = text.find(f"{name}=")
    if start < 0:
        return text
    end = len(text)
    for other in names[names.index(name) + 1:]:
        position = text.find(f"{other}=", start + 1)
        if position > start:
            end = min(end, position)
    return text[start:end]


def _cookie_expiry(header_value: str, name: str = "") -> str | None:
    segment = _segment_for(header_value, name) if name else (header_value or "")
    match = re.search(r"(?i)\bmax-age\s*=\s*(-?\d+)", segment)
    if match:
        return identity_mod.iso_in(int(match.group(1)))
    match = re.search(r"(?i)\bexpires\s*=\s*([^;,]+(?:,[^;]+)?)", segment)
    if match:
        try:
            return identity_mod.now_iso(
                email.utils.parsedate_to_datetime(match.group(1).strip()).timestamp())
        except (TypeError, ValueError, OverflowError):
            return None
    return None


def _dig(data, path: str):
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.lstrip("-").isdigit() and abs(int(part)) < len(current):
            current = current[int(part)]
        else:
            return None
    return current if isinstance(current, (str, int, float)) and not isinstance(current, bool) else None


def _capture(response: httpkit.HttpResponse, rule: str) -> tuple[str, str, str | None, str]:
    """Pull the credential out of a login response.

    Returns (value, field, expiry, how). An empty value means the rule matched
    nothing, which is a refusal and not a credential.
    """
    rule = (rule or "").strip()
    kind, _, argument = rule.partition(":")
    kind, argument = kind.strip().lower(), argument.strip()
    if kind in ("set-cookie", "cookie"):
        header_value = response.header("set-cookie")
        pairs = _parse_cookies(header_value)
        if argument:
            pairs = [(name, value) for name, value in pairs if name == argument]
        if not pairs:
            present = [name for name, _ in _parse_cookies(header_value)]
            return "", argument, None, (
                f"no cookie{f' {argument}' if argument else ''} in Set-Cookie"
                + (f"; the response set {present}" if present else
                   "; the response set no cookie at all")
                + (". Only the last Set-Cookie header of a response survives httpkit's header "
                   "dict, so a login that sets this cookie before another one cannot be captured "
                   "by name — capture it with json:<path>, header:<Name> or regex: instead, or "
                   "read it from the browser and record it with session.add"
                   if present and argument else ""))
        name, value = pairs[0]
        return value, name, _cookie_expiry(header_value, name), f"Set-Cookie {name}"
    if kind == "json":
        try:
            parsed = jsonlib.loads(response.body or "")
        except (ValueError, TypeError):
            return "", "", None, "the response body is not JSON"
        found = _dig(parsed, argument)
        return ("" if found is None else str(found)), "", None, f"JSON field {argument}"
    if kind == "header":
        return response.header(argument), "", None, f"response header {argument}"
    if kind == "regex":
        try:
            match = re.search(argument, response.body or "")
        except re.error as error:
            return "", "", None, f"bad regex: {error}"
        if not match:
            return "", "", None, f"regex {argument!r} matched nothing"
        return (match.group(1) if match.groups() else match.group(0)), "", None, f"regex {argument!r}"
    return "", "", None, (f"unknown capture rule {rule!r}; use set-cookie, set-cookie:<name>, "
                          f"json:<dotted.path>, header:<Name> or regex:<pattern with one group>")


def _body_shape(body: str | None, json_body: dict | None) -> str:
    """A login body's field names, never its values. The password is in there."""
    if json_body:
        return "json fields: " + ", ".join(sorted(str(k) for k in json_body))
    if body:
        pairs = urllib.parse.parse_qsl(body, keep_blank_values=True)
        if pairs:
            return "form fields: " + ", ".join(sorted({name for name, _ in pairs}))
        return f"{len(body)} bytes, not form-encoded"
    return "no body"


def _do_login(name: str, url: str, method: str, body: str | None,
              json_body: dict | None, success: str, capture: str, scheme: str, field: str,
              timeout: int, tool: str) -> tuple[dict, dict]:
    """The login request, the success check and the capture. Returns
    (outcome, evidence). Shared by session.login and session.refresh so there is
    one place that decides what a successful login looks like."""
    response = httpkit.request(method or "POST", url, data=body or None, json_body=json_body,
                               timeout=timeout or 15)
    headers_text = jsonlib.dumps(response.headers, ensure_ascii=False)
    marker_present = bool(success) and (success in (response.body or "") or success in headers_text)
    value, captured_field, expires, how = ("", "", None, "not attempted")
    if marker_present:
        value, captured_field, expires, how = _capture(response, capture)

    refusal = ""
    if response.status is None:
        refusal = "no-response"
    elif not marker_present:
        refusal = "success-marker-absent"
    elif not value:
        refusal = "capture-empty"

    chosen_scheme = (scheme or ("cookie" if (capture or "").strip().lower().startswith(
        ("set-cookie", "cookie")) else "bearer")).strip().lower()
    chosen_field = field or captured_field

    # The evidence is built by hand rather than from to_evidence(): a login
    # request body holds a password, and the only honest way to keep it out of
    # the ledger is never to put it there. The field names are recorded instead,
    # which is what a reviewer needs to know what was replayed.
    evidence = {
        "kind": "probe", "tool": tool, "target": url,
        "request": {"method": (method or "POST").upper(), "url": url,
                    "body": _body_shape(body, json_body),
                    "headers": {"note": "withheld: a login request carries a password"}},
        "response": {"status": response.status, "headers": response.headers,
                     "body_span": (response.body or "")[:4000], "length": response.length,
                     "time_ms": response.time_ms, "final_url": response.final_url,
                     "error": response.error},
        # `actor` is set by the caller, and only when an identity was actually
        # stored: a record saying `actor: ghost` for a login that stored nothing
        # names a caller this engagement cannot make requests as.
        "extracted": {"identity_name": name, "success_marker": success,
                      "success_marker_present": marker_present,
                      "capture_rule": capture, "capture_result": how,
                      "stored": not refusal, "refusal": refusal or None,
                      "credential_withheld": True},
    }
    outcome = {"response": response, "value": value, "field": chosen_field,
               "scheme": chosen_scheme, "expires": expires, "how": how,
               "marker_present": marker_present, "refusal": refusal}
    return outcome, evidence


def _json_leaves(data, prefix: str = "", depth: int = 0) -> list[tuple[str, str]]:
    """(dotted path, string value) for every string leaf of a JSON body.

    Bounded at 64 leaves and six levels: a login response is small, and an
    unbounded walk over a body an application chose is not a measurement.
    """
    if depth > 6:
        return []
    found: list[tuple[str, str]] = []
    if isinstance(data, dict):
        items = list(data.items())[:64]
    elif isinstance(data, list):
        items = [(str(index), value) for index, value in enumerate(data[:64])]
    else:
        return [(prefix, data)] if isinstance(data, str) else []
    for key, value in items:
        path = f"{prefix}.{key}" if prefix else str(key)
        found.extend(_json_leaves(value, path, depth + 1))
        if len(found) >= 64:
            break
    return found[:64]


def _credential_shapes(response: httpkit.HttpResponse, captured: str, name: str,
                       succeeded: bool) -> list[tuple[str, str]]:
    """Every value in a login response that could be the credential it returned.

    A login response that succeeded carries the credential by construction, so
    the unit to withhold there is not "the value we captured" but "everything
    shaped like what we came to collect". Withholding only the captured value
    left the rest on disk, which was measured rather than assumed: a login
    setting a session cookie and then a CSRF cookie, captured with
    `set-cookie:sid`, wrote the second cookie into the evidence record verbatim,
    and a `capture` rule pointing at the wrong JSON field wrote the token it had
    failed to capture — under a record whose own `extracted.stored` said
    `false`. `argus.util.redact` catches neither: it knows the shape of an API
    key, not of a session id.

    Three limits, each one a choice rather than an oversight:

    * A cookie value is withheld whatever the response said, because a
      Set-Cookie header has only one kind of content.
    * A string in a JSON body is withheld only when the success marker was
      present. When it was absent the login failed as far as anything here can
      tell, nothing was issued, and the body is the only diagnostic a model has
      for fixing `success` — withholding it would cost that and protect nothing.
      The residual case is a login that *did* succeed under a wrong marker: its
      body reaches the ledger, and its cookies still do not.
    * Under TOKEN_FLOOR characters a JSON string is a username or a status word
      as often as a token, so it is left alone. Withholding `"ok"` would cost a
      reviewer the body and gain nothing.
    """
    pairs: list[tuple[str, str]] = []
    for cookie, value in _parse_cookies(response.header("set-cookie")):
        pairs.append((value, f"<credential-shaped:cookie {cookie}>"))
    if succeeded:
        try:
            parsed = jsonlib.loads(response.body or "")
        except (ValueError, TypeError):
            parsed = None
        if parsed is not None:
            for path, value in _json_leaves(parsed):
                if len(value) >= TOKEN_FLOOR:
                    pairs.append((value, f"<credential-shaped:{path}>"))
    if captured:
        pairs.append((captured, f"<credential:{name}>"))
    # Longest first, so a fuller form is withheld before a prefix of it, and
    # deduplicated on the value so the captured placeholder wins its own value.
    seen: dict[str, str] = {}
    for value, placeholder in sorted(pairs, key=lambda pair: len(pair[0]), reverse=True):
        seen.setdefault(value, placeholder)
    if captured:
        seen[captured] = f"<credential:{name}>"
    return sorted(seen.items(), key=lambda pair: len(pair[0]), reverse=True)


def _scrub_login(evidence: dict, pairs: list[tuple[str, str]]) -> dict:
    """The login record is the one place a response must be scrubbed as well as
    a request: the credential is in its Set-Cookie header or its body, which is
    why we sent the request at all."""
    if not pairs:
        return evidence
    evidence["response"] = _withhold(evidence["response"], pairs)
    evidence["request"] = _withhold(evidence["request"], pairs)
    return evidence


@SERVER.tool(
    "session.login",
    "Obtain an identity by replaying a login request, and store the credential it returns. `success` "
    "is a substring that must appear in a successful response's body or headers; `capture` says "
    "which part of the response carries the credential. Nothing is stored unless the success marker "
    "is present AND the capture found a value — a login that silently failed is worse than no "
    "identity, because every later probe then runs anonymously while the ledger says it ran as this "
    "identity. The login body is never written to evidence; its field names are.",
    {"properties": {
        "name": {"type": "string", "description": "the identity to create or replace"},
        "url": {"type": "string", "description": "the login endpoint; must be in scope"},
        "success": {"type": "string",
                    "description": "a substring that appears only on success: a username, a "
                                   "dashboard string, or the Location of the post-login redirect"},
        "capture": {"type": "string",
                    "description": "set-cookie | set-cookie:<name> | json:<dotted.path> | "
                                   "header:<Name> | regex:<pattern with one group>"},
        "method": {"type": "string", "enum": ["POST", "GET", "PUT"]},
        "body": {"type": "string", "description": "form-encoded login body"},
        "json_body": {"type": "object", "description": "login body sent as application/json"},
        "scheme": {"type": "string", "enum": list(identity_mod.SCHEMES),
                   "description": "how the captured credential is then USED. "
                                  "Default: cookie for a set-cookie capture, bearer otherwise. "
                                  + _SCHEME_HELP},
        **_IDENTITY_FIELDS,
        "timeout": {"type": "integer"},
    }, "required": ["name", "url", "success", "capture"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="authenticate",
)
def login(context: ToolContext, name: str, url: str, success: str, capture: str,
          method: str = "POST", body: str = "", json_body: dict | None = None,
          scheme: str = "", field: str = "", note: str = "", entitled_to: list | None = None,
          not_entitled_to: list | None = None, timeout: int = 15) -> dict:
    if not context.engagement:
        return _no_engagement()
    outcome, evidence = _do_login(name, url, method, body, json_body, success, capture,
                                  scheme, field, timeout, "session.login")
    response = outcome["response"]
    withheld = _credential_shapes(response, outcome["value"], name, outcome["marker_present"])
    evidence = _scrub_login(evidence, withheld)
    # The same withholding applies to what the model is shown. A refusal prints
    # the response so the capture rule can be corrected, and on the refusal that
    # matters — marker present, capture empty — the credential is in that body.
    shown = _withhold((response.body or "")[:2000], withheld)

    if outcome["refusal"]:
        reasons = {
            "no-response": f"the login endpoint did not answer: {response.error}",
            "success-marker-absent": (f"{success!r} is not in the response ({_shape(response)}), so "
                                      f"this login failed or the marker is wrong"),
            "capture-empty": f"the login succeeded but {outcome['how']}",
        }
        return {
            "summary": (f"NO IDENTITY STORED for {name!r}: {reasons[outcome['refusal']]}"),
            "result": "no-signal",
            "data": {"stored": False, "refusal": outcome["refusal"], "status": response.status,
                     "success_marker_present": outcome["marker_present"],
                     "capture_result": outcome["how"],
                     "cookies_set": [cookie for cookie, _ in
                                     _parse_cookies(response.header("set-cookie"))],
                     "identities": _store(context).names()},
            "output": shown,
            "evidence": evidence,
            "next": ("read the response above and correct `success` or `capture`, or the "
                     "credentials in the body. Do not probe as this identity: it does not exist, "
                     "and a probe that claims it does would record an anonymous request as an "
                     "authenticated one"),
        }

    try:
        identity = identity_mod.Identity(
            name=name, scheme=outcome["scheme"], field=outcome["field"], value=outcome["value"],
            note=note or f"obtained from {url} by session.login", expires=outcome["expires"],
            entitled_to=tuple(entitled_to or ()), not_entitled_to=tuple(not_entitled_to or ()),
            renew={"url": url, "method": (method or "POST").upper(), "body": body or "",
                   "json_body": json_body, "success": success, "capture": capture,
                   "scheme": outcome["scheme"], "field": outcome["field"]})
        identity_mod.put(context.engagement, identity)
    except ValueError as error:
        return {"ok": False, "error": "bad-identity",
                "message": f"the login succeeded and the capture found a value, but the identity "
                           f"would be invalid: {error}",
                "evidence": evidence, "next": "pass scheme= and field= explicitly"}

    shape = identity.describe()
    evidence["extracted"]["identity"] = shape
    evidence["actor"] = identity.name
    store = _store(context)
    return {
        "summary": (f"identity {name!r} obtained from {url}: {outcome['how']} -> {shape['scheme']}"
                    + (f":{shape['field']}" if shape["field"] else "")
                    + f", {shape['value_length']} chars"
                    + (f" ending {shape['last4']}" if shape["last4"] else "")
                    + (f", expires {shape['expires']}" if shape["expires"] else "")),
        "result": "signal",
        "data": {"stored": True, "identity": shape, "status": response.status,
                 "capture_result": outcome["how"], "identities": store.names()},
        "output": "\n".join(i.line() for i in store.all()),
        "evidence": evidence,
        "next": ("session.probe_as issues requests as this identity, and session.refresh replays "
                 "this same login when it expires. For an authorization class, obtain the second "
                 "identity now — compare_as needs two named ones plus the unauthenticated control"),
    }


@SERVER.tool(
    "session.refresh",
    "Re-run the stored login for an identity and replace its credential, keeping its entitlements, "
    "its note and its login recipe. Only an identity obtained by session.login can be refreshed: "
    "one added with session.add recorded no way of obtaining it again, and this tool will not "
    "invent one. The same refusals apply — a refresh whose success marker is absent leaves the old "
    "credential in place rather than replacing it with nothing.",
    {"properties": {"name": {"type": "string"},
                    "url": {"type": "string",
                            "description": "the login endpoint again, as session.list prints it "
                                           "under renew_url. It is restated because the broker "
                                           "scope-checks the URL in the arguments before the "
                                           "request is built, and a tool that took its target only "
                                           "from a stored recipe would be a target the gate never "
                                           "saw. It must match the recipe"},
                    "timeout": {"type": "integer"}},
     "required": ["name", "url"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="authenticate",
)
def refresh(context: ToolContext, name: str, url: str, timeout: int = 15) -> dict:
    if not context.engagement:
        return _no_engagement()
    store = _store(context)
    identity = store.identities.get((name or "").strip().lower())
    if identity is None:
        return _unknown(name, store)
    recipe = identity.renew
    if not recipe:
        return {"ok": False, "error": "not-renewable",
                "message": f"identity {identity.name!r} was recorded with session.add, so nothing "
                           f"here knows how it was obtained. Re-run session.add with a fresh value, "
                           f"or create it with session.login so it can be refreshed.",
                "data": {"identity": identity.describe()},
                "next": "session.login name=" + identity.name}
    if url != recipe["url"]:
        return {"ok": False, "error": "url-mismatch",
                "message": f"url={url!r} is not the endpoint this identity was obtained from "
                           f"({recipe['url']!r}). The scope gate checked the URL you passed, so "
                           f"replaying a different one would be a request the gate never saw.",
                "data": {"identity": identity.describe()},
                "next": f"session.refresh name={identity.name} url={recipe['url']}"}

    outcome, evidence = _do_login(identity.name, recipe["url"], recipe.get("method", "POST"),
                                  recipe.get("body"), recipe.get("json_body"), recipe["success"],
                                  recipe["capture"], recipe.get("scheme", ""),
                                  recipe.get("field", ""), timeout, "session.refresh")
    response = outcome["response"]
    withheld = _credential_shapes(response, outcome["value"], identity.name,
                                   outcome["marker_present"])
    evidence = _scrub_login(evidence, withheld)
    if outcome["refusal"]:
        return {
            "summary": (f"refresh of {identity.name!r} FAILED ({outcome['refusal']}): the stored "
                        f"credential is unchanged. Login returned {_shape(response)}"),
            "result": "no-signal",
            "data": {"stored": False, "refusal": outcome["refusal"],
                     "identity": identity.describe(), "capture_result": outcome["how"]},
            "output": _withhold((response.body or "")[:2000], withheld),
            "evidence": evidence,
            "next": ("the login that worked before does not work now: the credentials changed, the "
                     "endpoint changed, or there is a rate limit or a lockout in front of it. Read "
                     "the response before replaying it again — a retry loop against a login "
                     "endpoint is how an engagement locks an account out"),
        }

    updated = identity_mod.update(context.engagement, identity.name, value=outcome["value"],
                                  field=outcome["field"] or identity.field,
                                  obtained=now_iso(), expires=outcome["expires"])
    shape = updated.describe()
    evidence["extracted"]["identity"] = shape
    evidence["actor"] = updated.name
    return {
        "summary": (f"identity {updated.name!r} refreshed: {outcome['how']}, "
                    f"{shape['value_length']} chars"
                    + (f" ending {shape['last4']}" if shape["last4"] else "")
                    + (f", expires {shape['expires']}" if shape["expires"] else "")),
        "result": "signal",
        "data": {"stored": True, "identity": shape},
        "output": "\n".join(i.line() for i in _store(context).all()),
        "evidence": evidence,
        "next": "re-issue the request that returned 401; if it still does, the rejection is not expiry",
    }


# --- probing as one ----------------------------------------------------------

@SERVER.tool(
    "session.probe_as",
    "Issue one request as a named identity and report the response. The identity supplies its own "
    "credential, and `actor` is written into the evidence record automatically — that field is what "
    "the differential verifier reads, and an authorization probe that omits it cannot be graded. "
    "Use identity=unauthenticated for the control: it always exists and needs no credential, and a "
    "privileged resource that answers it has no bypass to prove, only missing authorisation.",
    {"properties": {
        "identity": {"type": "string", "description": "a name from session.list"},
        "url": {"type": "string", "description": "absolute URL; must be in scope"},
        "accessed_subject": {"type": "string",
                             "description": "whose data this URL belongs to, if it is not the "
                                            "actor's own. The response rarely names the owner, so "
                                            "this is the only way the record can"},
        **_REQUEST_FIELDS,
    }, "required": ["identity", "url"]},
    tier=config.TIER_ACTIVE, step="identity-probe",
)
def probe_as(context: ToolContext, identity: str, url: str, accessed_subject: str = "",
             method: str = "GET", params: dict | None = None, headers: dict | None = None,
             body: str = "", json_body: dict | None = None, note: str = "",
             timeout: int = 15) -> dict:
    if not context.engagement:
        return _no_engagement()
    store = _store(context)
    actor = store.get(identity)
    if actor is None:
        return _unknown(identity, store)
    conflict = _header_conflict(headers, actor)
    if conflict:
        return conflict
    response, taken = _issue(actor, url, method, headers, params, body, json_body, timeout)
    entitlement = actor.entitlement(accessed_subject) if accessed_subject else "not-claimed"
    evidence = _record(actor, response, "session.probe_as", accessed_subject=accessed_subject,
                       note=note, extracted={"entitlement": entitlement,
                                             "identity_stale": actor.stale(),
                                             "identity_param_replaced": list(taken)})
    rejected = response.status in (401, 403)
    cross = bool(accessed_subject) and accessed_subject != actor.name
    succeeded = response.status is not None and response.status < 400
    control_answered = actor.name == identity_mod.UNAUTHENTICATED and succeeded
    return {
        "summary": (f"as {actor.name} ({actor.scheme}): {_shape(response)}"
                    + (f" | subject {accessed_subject} ({entitlement})" if accessed_subject else "")
                    + (" | the stored credential is past its recorded expiry" if actor.stale() else "")
                    + (f" | the url already named {', '.join(taken)}; the identity's own value "
                       f"replaced it" if taken else "")),
        "result": "signal" if succeeded else "no-signal",
        "data": {"actor": actor.name, "identity": actor.describe(), "status": response.status,
                 "length": response.length, "time_ms": response.time_ms,
                 "content_type": response.header("content-type"),
                 "location": response.header("location"),
                 "accessed_subject": accessed_subject or None, "entitlement": entitlement},
        "output": (response.body or "")[:6000],
        "evidence": evidence,
        "next": (("the control answered: this resource returns content to a request carrying no "
                  "credential at all. Before probing per-object authorization, record that — a "
                  "whole endpoint with no authentication is the larger finding, and this is the "
                  "observation that stops a token being credited for a door that was never locked"
                  if control_answered else
                  "the identity was rejected. If it is stale, session.refresh; if it is not, the "
                  "rejection is the control for this endpoint and belongs in the evidence set"
                  if rejected else
                  "this is a cross-read: session.compare_as issues it as both identities and as "
                  "unauthenticated, takes the entitlement control, and grades the set — one probe "
                  "instead of four"
                  if cross else
                  "one identity, one resource: this fixes what an authorised answer looks like. "
                  "The class needs the cross-read next")
                 + ("" if entitlement != "undeclared" else
                    ". The entitlement is undeclared: session.add with not_entitled_to so the "
                    "finding can say why this read should have failed")),
    }


@SERVER.tool(
    "session.compare_as",
    "The authorization workhorse: issue the SAME request as two named identities and as "
    "unauthenticated, optionally also as the actor against the actor's own resource, and grade the "
    "four records against the idor requirement in one call. The cross-read is recorded with `actor` "
    "and `accessed_subject`; the unauthenticated response and the actor's own-resource response are "
    "recorded as controls. A cross-read without its control is the single most common way an "
    "automated tester invents broken access control, so this tool takes the controls itself rather "
    "than trusting that a later call will. Four requests, one probe against the class budget.",
    {"properties": {
        "actor": {"type": "string",
                  "description": "the identity that should NOT be able to read the resource"},
        "other": {"type": "string",
                  "description": "the second identity, normally the owner. Its answer is what an "
                                 "authorised read looks like"},
        "url": {"type": "string", "description": "the resource under test; must be in scope"},
        "accessed_subject": {"type": "string",
                             "description": "whose data the URL belongs to. From an argument "
                                            "because the response rarely names the owner"},
        "own_url": {"type": "string",
                    "description": "the same endpoint for the ACTOR's own resource. This is the "
                                   "entitlement control: it shows the actor's authorised answer, so "
                                   "the cross-read is not compared against nothing. A second "
                                   "target, so it is scope-checked separately"},
        **_REQUEST_FIELDS,
        # Narrower than _REQUEST_FIELDS on purpose: this request is issued four
        # times, and a write issued four times measures the order of the
        # requests. A model shown an argument fills it, so the ones that are
        # refused are not offered.
        "method": {"type": "string", "enum": ["GET", "POST", "HEAD", "OPTIONS"],
                   "description": "the same method for all four requests. A write is refused: "
                                  "repeating it as four identities measures what the first one "
                                  "left behind, not authorization"},
    }, "required": ["actor", "other", "url", "accessed_subject"]},
    tier=config.TIER_ACTIVE, step="cross-read",
)
def compare_as(context: ToolContext, actor: str, other: str, url: str, accessed_subject: str,
               own_url: str = "", method: str = "GET", params: dict | None = None,
               headers: dict | None = None, body: str = "", json_body: dict | None = None,
               note: str = "", timeout: int = 15, vuln_class: str = "") -> dict:
    if not context.engagement:
        return _no_engagement()
    store = _store(context)
    first, second = store.get(actor), store.get(other)
    if first is None:
        return _unknown(actor, store)
    if second is None:
        return _unknown(other, store)
    if first.name == second.name:
        return {"ok": False, "error": "one-identity",
                "message": f"actor and other are both {first.name!r}. The class is a statement "
                           f"about two callers; one caller cannot make it.",
                "next": "session.login or session.add for the second identity"}
    if first.name == identity_mod.UNAUTHENTICATED:
        # The control this tool takes is the same request with no credential. If
        # the actor *is* that request, the control is a second copy of the probe,
        # and a control that repeats the probe establishes nothing — the set
        # still graded `idor: proven` on three identical anonymous requests.
        return {"ok": False, "error": "actor-is-the-control",
                "message": f"actor={identity_mod.UNAUTHENTICATED!r} makes the control a repeat of "
                           f"the probe: both requests carry no credential, so the set would claim "
                           f"a per-object authorization flaw from one anonymous read.",
                "next": f"session.probe_as identity={identity_mod.UNAUTHENTICATED} is the right "
                        f"tool for that question. If it answers, the finding is that the endpoint "
                        f"requires no authentication at all — record that, not idor. To compare two "
                        f"callers, name a credentialled identity as the actor"}
    if (method or "GET").upper() in ("PUT", "PATCH", "DELETE"):
        # This tool issues its request four times, as four callers. Repeating a
        # write is not a comparison: the second caller is answered by whatever
        # the first one left behind, so the differential measures the order of
        # the requests rather than anyone's authorization. The safety reading is
        # the same one — four writes to an object the engagement enabled only
        # `active` for — and both say no.
        return {"ok": False, "error": "method-not-comparable",
                "message": f"{(method or 'GET').upper()} would be issued four times, as four "
                           f"identities, against the same object. A repeated write measures the "
                           f"order of the requests, not authorization, and it changes state under "
                           f"a tool declared `active`.",
                "next": "compare the read first: GET, HEAD, OPTIONS or a POST-shaped read. A state "
                        "change belongs to the csrf requirement — read, act, read again — with "
                        "session.probe_as issuing the act as one named identity"}
    if own_url:
        # The gate scope-checks `url`, and only `url`. A tool that takes a second
        # URL and does not check it is a scope bypass that needs no exploit: the
        # control request would go wherever the argument said, under the
        # engagement's authority.
        allowed = context.state.scope.check(own_url)
        if not allowed:
            return {"ok": False, "error": "out-of-scope", "refused_by": "ledger",
                    "message": f"own_url is a second target and is checked separately: "
                               f"{allowed.reason}",
                    "next": "drop own_url, or add that target to the scope first. Without it the "
                            "set still grades, with the unauthenticated request as its only control"}
        if own_url == url:
            # The record would be filed as the actor's own authorised answer
            # while carrying the subject's object: a control that is the probe
            # again, under a label that says otherwise.
            return {"ok": False, "error": "own-url-is-the-target",
                    "message": "own_url is the same URL as the cross-read, so the entitlement "
                               "control would be the probe repeated and recorded as the actor's "
                               "own resource.",
                    "next": "pass the actor's own object — the same endpoint with the actor's own "
                            "id — or drop own_url and let the unauthenticated request be the control"}
    anonymous = store.get(identity_mod.UNAUTHENTICATED)
    conflict = _header_conflict(headers, first, second)
    if conflict:
        return conflict
    taken: set[str] = set()

    def send(identity, target):
        response, replaced = _issue(identity, target, method, headers, params, body, json_body,
                                    timeout)
        taken.update(replaced)
        return response

    actor_response = send(first, url)
    other_response = send(second, url)
    anon_response = send(anonymous, url)
    own_response = send(first, own_url) if own_url else None

    # Baseline is the authorised read, variant is the cross-read: a similarity of
    # 1.0 means the actor received the owner's data byte for byte, which is the
    # strongest form this observation takes.
    against_owner = httpkit.compare(other_response, actor_response)
    against_anonymous = httpkit.compare(anon_response, actor_response)
    entitlement = first.entitlement(accessed_subject)

    cross = _record(first, actor_response, "session.compare_as",
                    accessed_subject=accessed_subject, note=note or "the cross-read",
                    extracted={"entitlement": entitlement,
                               "declared_not_entitled": list(first.not_entitled_to),
                               "against_owner": against_owner.to_dict(),
                               "against_unauthenticated": against_anonymous.to_dict()})
    owner_record = _record(second, other_response, "session.compare_as",
                           accessed_subject=accessed_subject,
                           note="the authorised read: what this resource returns to the identity "
                                "that may have it",
                           extracted={"entitlement": second.entitlement(accessed_subject)})
    anon_record = _record(anonymous, anon_response, "session.compare_as",
                          kind="control", is_control=True, accessed_subject=accessed_subject,
                          note="control: the same request with no credential at all")
    records = [cross, owner_record, anon_record]
    if own_response is not None:
        records.append(_record(first, own_response, "session.compare_as", kind="control",
                               is_control=True, accessed_subject=first.name,
                               note="control: the actor's own resource, which fixes what an "
                                    "authorised answer looks like for this actor"))

    # What this tool collects is an authorization comparison: two identities, a
    # cross-read that names the subject, and two controls. So it grades `idor`
    # and nothing else, even when the hypothesis names another differential
    # class. An earlier version graded whatever the hypothesis named, and the
    # matrix let it through: with one status differing, this exact record set
    # graded `race-condition` and `cache-poisoning` as **proven**, though no
    # record here carries an `ordering`, nothing was requested twice and no
    # second requester was involved. A tool that hands back a grade for an
    # observation it never made is the one failure this system is arranged
    # against, and it is worse than a missing tool because it reads as a result.
    graded_as = "idor"
    verdict = matrix.verify(graded_as, records)
    named = matrix.spec_for(vuln_class or "")
    off_class = named.vuln_class if named and named.vuln_class != graded_as else ""

    anon_succeeded = anon_response.status is not None and anon_response.status < 400
    actor_succeeded = actor_response.status is not None and actor_response.status < 400
    got_owners_data = actor_succeeded and not _materially_different(against_owner)
    anon_same = anon_succeeded and not _materially_different(against_anonymous)

    rows = [f"{'actor':<16} {first.name:<14} {_shape(actor_response)}",
            f"{'other':<16} {second.name:<14} {_shape(other_response)}",
            f"{'control':<16} {anonymous.name:<14} {_shape(anon_response)}"]
    if own_response is not None:
        rows.append(f"{'control own':<16} {first.name:<14} {_shape(own_response)}")
    rows.append(f"cross-read vs owner: {against_owner.verdict} "
                f"(similarity {against_owner.body_similarity:.3f})")

    if not actor_succeeded:
        decision = (f"{first.name} was refused ({actor_response.status}) where {second.name} was "
                    f"not: access control held on this object. Falsify the hypothesis with this "
                    f"evidence id, or change one thing — another object id, another method, the "
                    f"parameter in a different place — and say which")
    elif anon_same:
        decision = ("the unauthenticated control got the same answer, so this endpoint enforces "
                    "nothing at all. That is a bigger finding than idor and a different one: "
                    "record missing authorisation on the endpoint, not a per-object flaw. These "
                    "records support it — the control is the proof")
    elif got_owners_data and verdict.proven:
        decision = (f"{first.name} read {accessed_subject}'s resource and got the owner's answer "
                    f"byte for byte, with the controls on record: the {graded_as} requirement is "
                    f"met. record_finding with these evidence ids")
    elif got_owners_data:
        decision = (f"the cross-read succeeded but the set is {verdict.grade}. Close this first: "
                    f"{', '.join(verdict.missing) or verdict.requirement}"
                    + ("" if own_url else
                       ". Pass own_url so the actor's own authorised answer is on record"))
    else:
        decision = (f"{first.name} got {actor_response.status} but not the owner's content "
                    f"(similarity {against_owner.body_similarity:.3f}): read the body before "
                    f"claiming anything. A 200 that says 'not found' or returns an empty object is "
                    f"the application refusing, in a shape a status code does not show")

    return {
        "summary": (f"{first.name} -> {_shape(actor_response)} | {second.name} -> "
                    f"{_shape(other_response)} | unauthenticated -> {_shape(anon_response)}"
                    + (f" | {first.name}'s own -> {_shape(own_response)}" if own_response else "")
                    + f" | {graded_as}: {verdict.grade}"
                    + (f" (the hypothesis names {off_class}; these records are not graded against "
                       f"it)" if off_class else "")
                    + (f" | the url already named {', '.join(sorted(taken))}; each identity's own "
                       f"value replaced it" if taken else "")),
        "result": "signal" if got_owners_data else "no-signal",
        "data": {"graded_as": graded_as, "proof_grade": verdict.grade,
                 "missing": verdict.missing, "checks": verdict.checks,
                 "hypothesis_class": (named.vuln_class if named else vuln_class),
                 "identity_param_replaced": sorted(taken),
                 "actor": first.name, "other": second.name,
                 "accessed_subject": accessed_subject, "entitlement": entitlement,
                 "statuses": {first.name: actor_response.status,
                              second.name: other_response.status,
                              anonymous.name: anon_response.status,
                              **({f"{first.name}-own": own_response.status} if own_response else {})},
                 "against_owner": against_owner.to_dict(),
                 "against_unauthenticated": against_anonymous.to_dict(),
                 "actor_received_owners_data": got_owners_data,
                 "unauthenticated_succeeded": anon_succeeded,
                 "control_count": sum(1 for r in records if r.get("is_control"))},
        "output": "\n".join(rows) + "\n\n--- as " + first.name + " ---\n"
                  + (actor_response.body or "")[:2000]
                  + "\n--- as " + second.name + " ---\n" + (other_response.body or "")[:2000]
                  + "\n--- unauthenticated ---\n" + (anon_response.body or "")[:1000],
        "evidence": cross,
        "extra_evidence": [record for record in records if record is not cross],
        "next": decision + ("" if entitlement != "undeclared" else
                            ". The entitlement is undeclared, so the report would have to say the "
                            "actor's lack of entitlement was assumed: declare it with session.add "
                            "not_entitled_to=[\"" + accessed_subject + "\"]")
                + ("" if not off_class else
                   f". These four records are an authorization comparison and are graded as idor "
                   f"only. The hypothesis is about {off_class}, which requires "
                   f"{named.requirement} — this tool issues each request once, records no "
                   f"ordering and involves no second requester, so nothing here bears on it. "
                   f"Do not record a {off_class} finding from these ids"),
    }
