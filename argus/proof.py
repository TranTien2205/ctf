"""The proof matrix: what each bug class must produce before it is a finding
rather than a candidate.

The rule this module exists to enforce:

    A scanner label, a template match, a timeout, a 500, a reflected payload
    and a plausible explanation are all *candidates*. A finding needs an
    observation that could not have happened if the vulnerability were absent.

`Session.add_finding` already refuses an excerpt that is not verbatim bytes
from a cited recorded exchange. That is necessary and not sufficient: it proves
the string was observed, not that the class was demonstrated. A benign page
reading `uid=1 selected` satisfies it for a claimed `rce`. So every finding is
also graded here, against a requirement written per class:

    proven      the requirement is met, controls included
    candidate   a class-specific signal exists, a control or an artifact is missing
    unproven    nothing in the cited evidence meets the requirement
    refused     the class may not be proven by this system at all

The grade never blocks the record - a candidate is worth reporting, it is just
not worth claiming. It is reported back to the agent with the names of the
checks that did not pass, so the next probe closes the gap instead of
re-proving what already passed.

Verifiers read only the recorded `request` and `response` of cited exchanges.
Two consequences, both deliberate:

  * A probe cannot self-report its way to `proven`. There is no `extracted`
    dict to trust - the checks re-read the bytes on the wire.
  * Scanner output is not class evidence. `run_external` and `mcp_call` record
    events that carry `output` and no `response`; a claim citing only those
    fails the wire check for every class, which is what the docs always said
    and nothing enforced.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Callable

GRADES = ("proven", "candidate", "unproven", "refused")

# --- signatures --------------------------------------------------------------

# Real `id` output, not the substring "uid=" that any ?uid=1 page carries:
# the parenthesised name, or uid and gid together.
IDENTITY_RE = re.compile(r"uid=\d+\([^)\n]{1,64}\)|uid=\d+\s+gid=\d+")
WINIDENT_RE = re.compile(r"(?i)\b(nt authority\\[a-z ]+|[a-z0-9_.-]+\\[a-z0-9_.-]+)\s*$", re.M)
# A command was actually sent - a separator followed by a benign read.
COMMAND_SENT_RE = re.compile(
    r"(?i)(?:[;|&\n]|\$\(|`|%0a|%3b|\|\|)\s*"
    r"(id|whoami|uname|hostname|echo|cat|type|set)\b")
DESTRUCTIVE_RE = re.compile(
    r"(?i)\b(rm\s+-rf|mkfs|dd\s+if=|shutdown|reboot|:\(\)\s*\{|useradd|"
    r"net\s+user\s+\S+\s+/add|nc\s+-e|bash\s+-i|/dev/tcp/|certutil\s+-urlcache|"
    r"invoke-webrequest\s+-outfile|chmod\s+777\s+/)")

DBMS_RE = re.compile(
    r"(?i)(sqlite3?\.\w*error|sqlite_master|you have an error in your sql syntax|"
    r"mysql_fetch|mariadb|psycopg2|pg::|postgresql|org\.postgresql|ORA-\d{5}|"
    r"microsoft (?:ole db|sql server)|sqlstate\[|sqlserverexception|"
    r"\d+\.\d+\.\d+-(?:mariadb|log)|sqlite version \d)")
TABLE_RE = re.compile(
    r"(?i)\b(?:from|join|into|update)\s+[`\"\[]?([a-z_][a-z0-9_.]*)[`\"\]]?"
    r"|\b(information_schema|sqlite_master|pg_catalog)\b")

PASSWD_RE = re.compile(r"root:.?:0:0:")
WIN_INI_RE = re.compile(r"(?i)\[(fonts|extensions|mci extensions|boot loader)\]")
PRIVKEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----")
FILE_SENTINELS = (("unix /etc/passwd", PASSWD_RE),
                  ("windows win.ini", WIN_INI_RE),
                  ("private key", PRIVKEY_RE))

SECRET_RE = re.compile(
    r"(?i)(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|eyJ[A-Za-z0-9_-]{10,}\."
    r"[A-Za-z0-9_-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?:api[_-]?key|secret[_-]?key|access[_-]?key|client[_-]?secret|password|"
    r"passwd|db[_-]?pass|token)\s*[:=]\s*\S{6,})")

# {{7*7}} / ${7*7} / #{7*7} / {{ 7 * 7 }} - the arithmetic form is the one a
# reflection cannot fake: the product has to be computed by the engine.
TEMPLATE_MATH_RE = re.compile(
    r"(\{\{|\$\{|#\{|\{%|\*\{)\s*(\d{1,6})\s*([*+])\s*(\d{1,6})\s*(\}\}|\}|%\})")

OBJECT_REF_RE = re.compile(r"(?i)(?:^|[/?&])(?:id|uid|user_?id|order|account|"
                           r"doc|object|num|pk)=(\w{1,64})|/(\d{1,12})(?:/|$)")


# --- the claim ---------------------------------------------------------------

@dataclass
class Claim:
    """One recorded finding, as the verifiers see it: the quoted bytes plus the
    exchanges the author cited. Nothing else - an uncited exchange is not
    evidence even when it sits in the same transcript."""
    excerpt: str
    entries: list[dict] = field(default_factory=list)

    @property
    def exchanges(self) -> list[dict]:
        """Cited entries that carry a real request/response pair."""
        return [e for e in self.entries
                if isinstance(e, dict) and isinstance(e.get("response"), dict)]

    @property
    def events(self) -> list[dict]:
        return [e for e in self.entries
                if isinstance(e, dict) and not isinstance(e.get("response"), dict)]


def req_text(entry: dict) -> str:
    req = entry.get("request") or {}
    if not isinstance(req, dict):
        return ""
    parts = [str(req.get("method") or ""), str(req.get("url") or ""),
             str(req.get("headers") or ""), str(req.get("body") or ""),
             str(req.get("request_text") or "")]
    return urllib.parse.unquote_plus(" ".join(p for p in parts if p))


def resp_body(entry: dict) -> str:
    resp = entry.get("response") or {}
    return str(resp.get("body") or "") if isinstance(resp, dict) else ""


def resp_text(entry: dict) -> str:
    resp = entry.get("response") or {}
    if not isinstance(resp, dict):
        return ""
    return "\n".join([str(resp.get("status") or ""),
                      str(resp.get("headers") or ""), resp_body(entry)])


def header_of(entry: dict, name: str) -> str:
    resp = entry.get("response") or {}
    headers = resp.get("headers") if isinstance(resp, dict) else None
    if not isinstance(headers, dict):
        return ""
    for key, value in headers.items():
        if str(key).lower() == name.lower():
            return str(value)
    return ""


def status_of(entry: dict) -> int:
    resp = entry.get("response") or {}
    try:
        return int(resp.get("status") or 0) if isinstance(resp, dict) else 0
    except (TypeError, ValueError):
        return 0


def _check(name: str, ok: bool, detail: str = "") -> dict:
    return {"check": name, "ok": bool(ok), "detail": detail}


def _grade(checks: list[dict], required: tuple[str, ...],
           veto: tuple[str, ...] = (), floor: tuple[str, ...] = ()) -> str:
    """`candidate` means partial progress on the requirement itself.

    A veto disqualifies; it never carries a grade. "The proof command stayed
    benign" passes trivially when no command ran, so as a required check it
    would make any record under an rce hypothesis a critical candidate.

    A floor check is the one that makes the evidence ABOUT this class at all.
    Without it a record set holding only the control graded `candidate`.
    """
    passed = {c["check"] for c in checks if c["ok"]}
    for name in (*veto, *floor):
        if name not in passed:
            return "unproven"
    if required and all(name in passed for name in required):
        return "proven"
    return "candidate" if any(name in passed for name in required) else "unproven"


# --- shared checks -----------------------------------------------------------

def _wire_check(claim: Claim) -> dict:
    """Every class needs bytes from the wire. A claim citing only scanner or
    MCP output cites a tool's opinion."""
    ok = bool(claim.exchanges)
    detail = "" if ok else (
        f"the only cited evidence is {len(claim.events)} non-HTTP event(s) "
        "(scanner/MCP output); re-verify with http_request and cite that")
    return _check("proof read from the wire", ok, detail)


def _discriminates(claim: Claim, name: str = "the excerpt discriminates against a control") -> dict:
    """The quoted bytes appear in one cited response and are absent from
    another. This is what separates a difference from boilerplate: `"username"`
    is in every profile page, including the author's own."""
    bodies = [(e.get("id"), resp_body(e)) for e in claim.exchanges]
    present = [rid for rid, body in bodies if claim.excerpt and claim.excerpt in body]
    absent = [rid for rid, body in bodies if not claim.excerpt or claim.excerpt not in body]
    ok = bool(present and absent)
    if ok:
        detail = f"present in {present[0]}, absent from {absent[0]}"
    elif len(bodies) < 2:
        detail = "only one exchange cited; a difference needs its control"
    else:
        detail = "the excerpt is in every cited response - that is boilerplate, not a difference"
    return _check(name, ok, detail)


def _object_refs(entry: dict) -> set[str]:
    url = str((entry.get("request") or {}).get("url") or "")
    refs = set()
    for m in OBJECT_REF_RE.finditer(url):
        refs.add(m.group(1) or m.group(2))
    return {r for r in refs if r}


# --- verifiers ---------------------------------------------------------------

def verify_command_output(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Code execution. The identity line is what a reflection cannot fake."""
    checks = []
    sent = [e for e in claim.exchanges if COMMAND_SENT_RE.search(req_text(e))]
    checks.append(_check("a benign command was sent", bool(sent),
                         f"exchange {sent[0].get('id')}" if sent else
                         "no cited request carries a separator followed by a read-only "
                         "command (id/whoami/uname/echo)"))
    identity, reflected = None, None
    for entry in claim.exchanges:
        body = resp_body(entry)
        hit = IDENTITY_RE.search(body) or WINIDENT_RE.search(body)
        if not hit:
            continue
        # the same literal in the request means the target echoed our bytes
        if hit.group(0) in req_text(entry):
            reflected = entry
            continue
        identity = (hit.group(0), entry)
    checks.append(_check(
        "identity output returned by the target", identity is not None,
        f"{identity[0]!r} in {identity[1].get('id')}" if identity else
        (f"the identity line in {reflected.get('id')} is also in its own request - "
         "that is a reflection, not execution" if reflected else
         "no uid=N(...)/whoami line in any cited response. Echoing `id` back as "
         "text does not produce one")))
    marker = None
    for entry in sent:
        body, request = resp_body(entry), req_text(entry)
        for token in re.findall(r"[a-z0-9]{6,32}", request.lower()):
            if token in body.lower() and token not in ("whoami", "hostname"):
                marker, _ = token, None
                break
        if marker:
            break
    checks.append(_check("marker echoed in the output", marker is not None,
                         f"{marker!r}" if marker else
                         "no token from the probe appears in its own output; send "
                         "`id; echo <nonce>` so the nonce ties output to this probe"))
    destructive = [e.get("id") for e in claim.exchanges
                   if DESTRUCTIVE_RE.search(req_text(e))]
    checks.append(_check("proof command stayed benign", not destructive,
                         "" if not destructive else
                         f"{destructive} sent more than a read - the evidence is void"))
    return checks


def verify_data_extraction(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Injection into a data store. A named table and real rows out of it."""
    checks = []
    if spec.fingerprint:
        banner = next((DBMS_RE.search(resp_text(e)) for e in claim.exchanges
                       if DBMS_RE.search(resp_text(e))), None)
        checks.append(_check("data store fingerprinted", banner is not None,
                             banner.group(0)[:80] if banner else
                             "no engine named in any cited response; read @@version / "
                             "version() once, or cite the error that names it"))
    named = None
    for entry in claim.exchanges:
        m = TABLE_RE.search(req_text(entry))
        if m:
            named = (m.group(1) or m.group(2), entry)
            break
    checks.append(_check("a named table was queried", named is not None,
                         f"{named[0]} in {named[1].get('id')}" if named else
                         "no cited request names a table or information_schema - "
                         "a differential proves the channel, not the read"))
    extracted = None
    for entry in claim.exchanges:
        body = resp_body(entry)
        if not claim.excerpt or claim.excerpt not in body:
            continue
        if DBMS_RE.search(claim.excerpt):
            continue           # the engine's error message is not its data
        if TABLE_RE.search(req_text(entry)):
            extracted = entry
            break
    checks.append(_check("rows returned, not an error message", extracted is not None,
                         f"quoted from {extracted.get('id')}" if extracted else
                         "the excerpt is an error string, or the exchange it came from "
                         "never named a table. Quote a row"))
    rows = claim.excerpt.count("\n") + 1 if claim.excerpt else 0
    checks.append(_check("extraction stayed minimal", rows <= 20,
                         "" if rows <= 20 else
                         f"{rows} lines quoted - five rows is a proof, a dump is an incident"))
    return checks


def verify_file_read(claim: Claim, spec: "ProofSpec") -> list[dict]:
    checks, hit, control = [], None, None
    for entry in claim.exchanges:
        body = resp_body(entry)
        for label, pattern in FILE_SENTINELS:
            if pattern.search(body):
                hit = hit or (label, entry)
        if not any(p.search(body) for _, p in FILE_SENTINELS):
            control = control or entry
    checks.append(_check("known-file sentinel observed", hit is not None,
                         f"{hit[0]} in {hit[1].get('id')}" if hit else
                         "no /etc/passwd, win.ini or private-key signature in any "
                         "cited response"))
    checks.append(_check("negative control recorded", control is not None,
                         f"exchange {control.get('id')}" if control else
                         "cite a request for a path that does not exist, so the "
                         "sentinel is shown to come from the file and not the page"))
    return checks


def verify_template_eval(claim: Claim, spec: "ProofSpec") -> list[dict]:
    evaluated, echoed = None, None
    for entry in claim.exchanges:
        m = TEMPLATE_MATH_RE.search(req_text(entry))
        if not m:
            continue
        left, op, right = int(m.group(2)), m.group(3), int(m.group(4))
        product = str(left * right if op == "*" else left + right)
        body = resp_body(entry)
        literal = m.group(0)
        if literal in body:
            echoed = entry
        elif product in body and product != str(left) and product != str(right):
            evaluated = (literal, product, entry)
    return [_check(
        "expression evaluated, not echoed", evaluated is not None,
        f"{evaluated[0]} rendered as {evaluated[1]} in {evaluated[2].get('id')}"
        if evaluated else
        (f"{echoed.get('id')} returned the expression unchanged - that is reflection"
         if echoed else
         "no cited request carries an arithmetic template expression "
         "({{7*7}}); a payload that is merely reflected proves nothing"))]


def verify_differential(claim: Claim, spec: "ProofSpec") -> list[dict]:
    refs = set()
    for entry in claim.exchanges:
        refs |= _object_refs(entry)
    checks = [_check("two distinct object references requested", len(refs) >= 2,
                     f"{sorted(refs)}" if len(refs) >= 2 else
                     f"only {sorted(refs) or 'no'} object reference(s) cited - an "
                     "access-control claim needs the other actor's subject too")]
    present = [e.get("id") for e in claim.exchanges
               if claim.excerpt and claim.excerpt in resp_body(e)]
    checks.append(_check("another subject's data returned", bool(present),
                         f"in {present[0]}" if present else
                         "the quoted bytes are in no cited response"))
    checks.append(_discriminates(claim, "outcomes actually differ"))
    return checks


def verify_token_forgery(claim: Claim, spec: "ProofSpec") -> list[dict]:
    accepted, rejected = None, None
    for entry in claim.exchanges:
        creds = str((entry.get("request") or {}).get("headers") or "")
        bearing = bool(re.search(r"(?i)authorization|cookie|x-api-key|token", creds))
        code = status_of(entry)
        if bearing and 200 <= code < 300:
            accepted = accepted or entry
        if 401 <= code <= 403:
            rejected = rejected or entry
    privileged = [e.get("id") for e in claim.exchanges
                  if claim.excerpt and claim.excerpt in resp_body(e)
                  and 200 <= status_of(e) < 300]
    return [
        _check("a forged credential was accepted", accepted is not None,
               f"exchange {accepted.get('id')} returned {status_of(accepted)}"
               if accepted else
               "no cited exchange sends a credential and gets a 2xx"),
        _check("a deliberately invalid credential is rejected", rejected is not None,
               f"exchange {rejected.get('id')}" if rejected else
               "cite the control: the same request with a wrong signature must "
               "come back 401/403, or the endpoint simply needs no auth"),
        _check("privileged content returned", bool(privileged),
               f"in {privileged[0]}" if privileged else
               "the quoted bytes are in no accepted response"),
    ]


def verify_off_origin_redirect(claim: Claim, spec: "ProofSpec") -> list[dict]:
    off, control = None, None
    for entry in claim.exchanges:
        location = header_of(entry, "Location")
        if not location:
            continue
        req_host = (urllib.parse.urlparse(str((entry.get("request") or {})
                                              .get("url") or "")).hostname or "")
        dest = urllib.parse.urlparse(location if "//" in location
                                     else "//" + location.lstrip("/"), scheme="http")
        if dest.hostname and dest.hostname.lower() != req_host.lower():
            off = off or (location, entry)
        else:
            control = control or entry
    return [
        _check("the Location points off origin", off is not None,
               f"{off[0][:120]} in {off[1].get('id')}" if off else
               "no cited response carries a Location header leaving the origin"),
        _check("control recorded for the expected outcome", control is not None,
               f"exchange {control.get('id')}" if control else
               "cite the in-origin case too, so the parameter is shown to be "
               "honoured rather than ignored"),
    ]


def verify_unkeyed_input(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Cache poisoning / deception / smuggling: a value one requester sent came
    back to a requester that did not send it."""
    sent_by, served_to = None, None
    for entry in claim.exchanges:
        sends = bool(claim.excerpt) and claim.excerpt in req_text(entry)
        serves = bool(claim.excerpt) and claim.excerpt in resp_body(entry)
        if sends:
            sent_by = sent_by or entry
        if serves and not sends:
            served_to = served_to or entry
    # Both halves, in two different exchanges. "A response carries bytes its own
    # request did not send" is true of every page ever served, so on its own it
    # graded any excerpt a candidate - the pairing is the whole claim.
    paired = served_to is not None and sent_by is not None
    return [
        _check("the value reached a requester that did not send it", paired,
               f"sent in {sent_by.get('id')}, served to {served_to.get('id')}"
               if paired else
               ("the value is in no cited request - cite the poisoning request, "
                "otherwise this is an ordinary page and not a cache"
                if served_to is not None else
                "every cited response carrying the value was answering a request "
                "that sent it - that is an echo, not a cache")),
        _check("the injecting request is on record", sent_by is not None,
               f"exchange {sent_by.get('id')}" if sent_by else
               "cite the poisoning request as well as the victim read"),
    ]


def verify_cors(claim: Claim, spec: "ProofSpec") -> list[dict]:
    reflecting, creds = None, None
    for entry in claim.exchanges:
        allow = header_of(entry, "Access-Control-Allow-Origin")
        origin = ""
        headers = (entry.get("request") or {}).get("headers") or {}
        if isinstance(headers, dict):
            for k, v in headers.items():
                if str(k).lower() == "origin":
                    origin = str(v)
        if allow and origin and allow.strip() == origin.strip():
            reflecting = reflecting or (origin, entry)
        if header_of(entry, "Access-Control-Allow-Credentials").strip().lower() == "true":
            creds = creds or entry
    return [
        _check("the probe origin is reflected", reflecting is not None,
               f"{reflecting[0]} echoed in {reflecting[1].get('id')}" if reflecting else
               "no cited response echoes the Origin it was sent"),
        _check("credentials are allowed with it", creds is not None,
               f"exchange {creds.get('id')}" if creds else
               "without Access-Control-Allow-Credentials: true a reflected origin "
               "reads nothing authenticated - rate it info"),
    ]


def verify_state_change(claim: Claim, spec: "ProofSpec") -> list[dict]:
    reads = [e for e in claim.exchanges
             if str((e.get("request") or {}).get("method") or "GET").upper() == "GET"]
    writes = [e for e in claim.exchanges
              if str((e.get("request") or {}).get("method") or "GET").upper()
              in ("POST", "PUT", "PATCH", "DELETE")]
    return [
        _check("the state-changing request is on record", bool(writes),
               f"exchange {writes[0].get('id')}" if writes else
               "no cited request changes state"),
        _check("the state was read back", len(reads) >= 1,
               f"{len(reads)} read(s) cited" if reads else
               "cite the read that shows the change landed"),
        _discriminates(claim, "the readback differs from before"),
    ]


def verify_secret_leak(claim: Claim, spec: "ProofSpec") -> list[dict]:
    hit = SECRET_RE.search(claim.excerpt or "")
    in_response = [e.get("id") for e in claim.exchanges
                   if claim.excerpt and claim.excerpt in resp_body(e)]
    return [
        _check("a credential-shaped secret was observed", hit is not None,
               hit.group(0)[:24] + "..." if hit else
               "the quoted bytes do not look like a credential; quote the key, "
               "token or key-value line itself"),
        _check("it came from a response", bool(in_response),
               f"in {in_response[0]}" if in_response else
               "the quoted bytes are in no cited response"),
    ]


def verify_browser_execution(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Reflection is checkable from the bytes; execution is not.

    The signal is a metacharacter surviving unencoded into an HTML response -
    not the presence of a `<script>` tag nearby, which an early version looked
    for. A reflected-XSS payload BRINGS its own context; requiring the context
    to exist already failed the lab's own `<>'"&=/` canary, which is the
    textbook positive case.
    """
    reflected, encoded = None, None
    raw = [ch for ch in "<>\"'" if ch in (claim.excerpt or "")]
    for entry in claim.exchanges:
        body = resp_body(entry)
        if not claim.excerpt or claim.excerpt not in body:
            continue
        if not re.search(r"(?i)text/html|application/xhtml",
                         str(((entry.get("response") or {}).get("headers")) or "")):
            continue
        if raw:
            reflected = (entry, "".join(raw))
        elif re.search(r"&lt;|&gt;|&quot;|&#x?\d", body):
            encoded = entry
    return [
        _check("payload reflected unencoded into HTML", reflected is not None,
               f"{reflected[1]!r} survived into {reflected[0].get('id')}" if reflected
               else ("the response entity-encodes the payload - that is the fix "
                     f"working ({encoded.get('id')})" if encoded else
                     "the quoted bytes carry no raw < > \" ' and so cannot break out "
                     "of their context, or they are in no cited HTML response")),
        _check("a real browser executed it", False,
               "this system has no browser, so execution is not provable here. "
               "Drive one over mcp_call and cite the nonce it reports, or leave "
               "this a candidate and say so in the report"),
    ]


def verify_refused(claim: Claim, spec: "ProofSpec") -> list[dict]:
    return [_check("class is provable by this system", False, spec.refusal)]


def verify_generic(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Classes whose artifact is a measured difference and nothing more."""
    return [_discriminates(claim)]


# --- the matrix --------------------------------------------------------------

@dataclass
class ProofSpec:
    vuln_class: str
    requirement: str
    required: tuple[str, ...]
    verifier: Callable[[Claim, "ProofSpec"], list[dict]]
    veto: tuple[str, ...] = ()
    floor: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    fingerprint: bool = True
    refusal: str = ""
    notes: str = ""

    def verify(self, claim: Claim) -> "Verdict":
        wire = _wire_check(claim)
        if self.verifier is verify_refused:
            checks = self.verifier(claim, self)
            return Verdict(self.vuln_class, "refused", checks,
                           [c["check"] for c in checks], self.requirement, self.notes)
        if not wire["ok"]:
            return Verdict(self.vuln_class, "unproven", [wire], [wire["check"]],
                           self.requirement, self.notes)
        checks = [wire, *self.verifier(claim, self)]
        grade = _grade(checks, self.required, self.veto, self.floor)
        named = (*self.required, *self.veto, *self.floor)
        missing = [c["check"] for c in checks if not c["ok"] and c["check"] in named]
        return Verdict(self.vuln_class, grade, checks, missing,
                       self.requirement, self.notes)


@dataclass
class Verdict:
    vuln_class: str
    grade: str
    checks: list[dict] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    requirement: str = ""
    notes: str = ""

    @property
    def proven(self) -> bool:
        return self.grade == "proven"

    def to_dict(self) -> dict:
        out = {"vuln_class": self.vuln_class, "grade": self.grade,
               "requirement": self.requirement, "checks": self.checks}
        if self.missing:
            out["missing"] = self.missing
        return out

    def explain(self) -> str:
        lines = [f"{self.vuln_class}: {self.grade}", f"  requires: {self.requirement}"]
        for check in self.checks:
            lines.append(f"  [{'x' if check['ok'] else ' '}] {check['check']}"
                         + (f" - {check['detail']}" if check.get("detail") else ""))
        return "\n".join(lines)


RCE_REQUIRED = ("a benign command was sent", "identity output returned by the target",
                "marker echoed in the output")
RCE_VETO = ("proof command stayed benign",)
SQLI_REQUIRED = ("data store fingerprinted", "a named table was queried",
                 "rows returned, not an error message")
EXTRACTION_REQUIRED = ("a named table was queried", "rows returned, not an error message")

MATRIX: dict[str, ProofSpec] = {}


def _register(spec: ProofSpec) -> None:
    MATRIX[spec.vuln_class] = spec
    for alias in spec.aliases:
        MATRIX[alias] = spec


for _s in [
    ProofSpec("rce", "the output of `id; echo <nonce>` returned by the target, with "
              "the nonce tying the output to the probe",
              RCE_REQUIRED, verify_command_output, veto=RCE_VETO,
              floor=("identity output returned by the target",),
              aliases=("cmdinjection", "command-injection", "commandinjection",
                       "os-command-injection", "code-injection", "codeinjection",
                       "shell-injection"),
              notes="No shell, no download, no persistence. The nonce is the proof."),
    ProofSpec("deserialize", "code execution proven the way rce is, from a "
              "serialized payload",
              RCE_REQUIRED, verify_command_output, veto=RCE_VETO,
              floor=("identity output returned by the target",),
              aliases=("deserialization", "insecure-deserialization", "pickle",
                       "java-deserialization")),
    ProofSpec("sqli", "the DBMS fingerprint plus at least one row from a named "
              "table, bounded to what proves the read",
              SQLI_REQUIRED, verify_data_extraction,
              aliases=("sql-injection", "sqlinjection", "blind-sqli",
                       "second-order-sqli"),
              notes="Five rows is a proof. A full dump is an incident."),
    ProofSpec("nosqli", "documents returned from a named collection the query "
              "should not have reached",
              EXTRACTION_REQUIRED, verify_data_extraction, fingerprint=False,
              aliases=("nosql-injection", "mongo-injection")),
    ProofSpec("graphql", "a query returning records outside the caller's scope",
              EXTRACTION_REQUIRED, verify_data_extraction, fingerprint=False,
              aliases=("graphql-exposure",)),
    ProofSpec("lfi", "a sentinel from a file whose contents are known, plus a "
              "control path that does not exist",
              ("known-file sentinel observed", "negative control recorded"),
              verify_file_read, floor=("known-file sentinel observed",),
              aliases=("file-read", "fileread", "path-traversal", "pathtraversal",
                       "arbitrary-file-read", "directory-traversal", "rfi")),
    ProofSpec("xxe", "a local file read through the parser",
              ("known-file sentinel observed",), verify_file_read,
              aliases=("xml-external-entity",)),
    ProofSpec("ssti", "an arithmetic result rendered by the template engine, "
              "with the expression itself absent from the response",
              ("expression evaluated, not echoed",), verify_template_eval,
              aliases=("template-injection", "el-injection", "expression-injection")),
    ProofSpec("idor", "actor A reading actor B's subject, with the control "
              "showing the difference is the identity and not the page",
              ("two distinct object references requested",
               "another subject's data returned", "outcomes actually differ"),
              verify_differential, floor=("outcomes actually differ",),
              aliases=("bola", "authorization-bypass", "broken-access-control",
                       "access-control", "massassign", "massassignment",
                       "mass-assignment")),
    ProofSpec("jwt", "a forged or absent credential accepted on a privileged "
              "resource, with an invalid one rejected",
              ("a forged credential was accepted",
               "a deliberately invalid credential is rejected",
               "privileged content returned"),
              verify_token_forgery, floor=("a forged credential was accepted",),
              aliases=("auth-bypass", "authbypass", "jwt-forgery",
                       "session-fixation", "mfa-bypass", "auth")),
    ProofSpec("redirect", "a 3xx Location pointing off origin, with the in-origin "
              "control showing the destination parameter is honoured",
              ("the Location points off origin",
               "control recorded for the expected outcome"),
              verify_off_origin_redirect, floor=("the Location points off origin",),
              aliases=("open-redirect", "openredirect")),
    ProofSpec("cache", "a value only the poisoning request sent, returned to a "
              "requester that did not send it",
              ("the value reached a requester that did not send it",
               "the injecting request is on record"),
              verify_unkeyed_input,
              floor=("the value reached a requester that did not send it",),
              aliases=("cache-poisoning", "cachepoisoning", "web-cache-deception",
                       "cache-deception", "smuggle", "request-smuggling",
                       "requestsmuggling", "xfh", "host-header")),
    ProofSpec("cors", "the probe origin reflected in Access-Control-Allow-Origin "
              "with credentials allowed",
              ("the probe origin is reflected", "credentials are allowed with it"),
              verify_cors, floor=("the probe origin is reflected",)),
    ProofSpec("xss", "a headless browser executing the payload and reporting the "
              "probe nonce",
              ("payload reflected unencoded into HTML",
               "a real browser executed it"),
              verify_browser_execution,
              aliases=("reflected-xss", "stored-xss", "dom-xss", "reflection",
                       "ppoll", "prototype-pollution", "prototypepollution")),
    ProofSpec("csrf", "a cross-origin request changing state, read back afterwards",
              ("the state-changing request is on record", "the state was read back",
               "the readback differs from before"),
              verify_state_change, floor=("the readback differs from before",),
              aliases=("logic-flaw", "logicflaw", "business-logic", "race",
                       "race-condition", "racecondition", "toctou")),
    ProofSpec("disclosure", "the credential or source observed in a response, "
              "quoted as the bytes that leaked",
              ("a credential-shaped secret was observed", "it came from a response"),
              verify_secret_leak, floor=("a credential-shaped secret was observed",),
              aliases=("info-disclosure", "infodisclosure", "information-disclosure",
                       "secret-exposure", "source-leak", "credential-leak")),
    ProofSpec("ssrf", "a response only the internal network could have given, "
              "against the control that the same fetch from outside does not",
              ("the excerpt discriminates against a control",), verify_generic,
              aliases=("server-side-request-forgery", "blind-ssrf")),
    ProofSpec("enum", "the same request distinguishing a real account from an "
              "absent one, with both on record",
              ("the excerpt discriminates against a control",), verify_generic,
              aliases=("user-enumeration", "enumeration", "username-enum")),
    ProofSpec("crlf", "a header or body boundary the response honoured, with the "
              "clean control",
              ("the excerpt discriminates against a control",), verify_generic,
              aliases=("header-injection", "response-splitting")),
    ProofSpec("upload", "a file stored and served back with active content-type, "
              "proven by what the server executed or served",
              ("the excerpt discriminates against a control",), verify_generic,
              aliases=("file-upload", "unrestricted-file-upload")),
    ProofSpec("method", "a method the endpoint should refuse being honoured, with "
              "the refused control",
              ("the excerpt discriminates against a control",), verify_generic,
              aliases=("http-method", "verb-tampering", "trace")),
    ProofSpec("lockout", "repeated failures never refused, counted on record",
              ("the excerpt discriminates against a control",), verify_generic,
              aliases=("no-rate-limit", "bruteforce")),
    ProofSpec("websocket", "a message accepted across origin, with the control",
              ("the excerpt discriminates against a control",), verify_generic,
              aliases=("cswsh", "ws")),
    ProofSpec("dos", "this system does not prove availability impact",
              (), verify_refused,
              refusal="Denial of service is out of scope by construction: the proof "
                      "is the damage. Describe the mechanism from source or "
                      "configuration, generate no load.",
              aliases=("ddos", "resource-exhaustion", "zip-bomb", "slowloris")),
]:
    _register(_s)


CANDIDATE_ONLY = {
    "nuclei-match": "A template match names a candidate class. Re-verify under that class.",
    "nikto-finding": "A signature hit is a candidate. Re-verify under the class it implies.",
    "version-cve": "A version banner implies a CVE; exploitability is proven, not inferred.",
    "sqlmap": "sqlmap's verdict is a lead. Re-verify on the wire under sqli.",
}


def normalize(category: str) -> str:
    return re.sub(r"[^a-z0-9]", "-", str(category or "").strip().lower()).strip("-")


def canonical(category: str) -> str:
    """The class this category names, or the normalized text when it names none.

    This is also the dedup key: `SQLi`, `sql-injection` and `sqlinjection` are
    one class, so two workers cannot record the same bug twice by spelling it
    differently - which they could while the key was the author's free text.
    """
    key = normalize(category)
    spec = MATRIX.get(key) or MATRIX.get(key.replace("-", ""))
    return spec.vuln_class if spec else key


def spec_for(category: str) -> ProofSpec | None:
    key = normalize(category)
    return MATRIX.get(key) or MATRIX.get(key.replace("-", ""))


def classes() -> list[str]:
    return sorted({spec.vuln_class for spec in MATRIX.values()})


def requirement_of(category: str) -> str:
    spec = spec_for(category)
    return spec.requirement if spec else ""


def grade(category: str, excerpt: str, entries: list[dict]) -> Verdict:
    """Grade one claim. Never raises: a malformed transcript entry is evidence
    that does not pass a check, not a crash in the recorder."""
    claim = Claim(str(excerpt or ""), [e for e in (entries or []) if isinstance(e, dict)])
    spec = spec_for(category)
    if spec is None:
        hint = CANDIDATE_ONLY.get(normalize(category))
        return Verdict(normalize(category), "unproven",
                       [_check("class is in the proof matrix", False,
                               hint or f"no requirement is defined for "
                               f"{normalize(category)!r} - use one of: "
                               f"{', '.join(classes())}")],
                       ["class is in the proof matrix"], hint or "")
    try:
        return spec.verify(claim)
    except Exception as exc:                                  # pragma: no cover
        return Verdict(spec.vuln_class, "unproven",
                       [_check("evidence is readable", False, f"{type(exc).__name__}: {exc}")],
                       ["evidence is readable"], spec.requirement, spec.notes)
