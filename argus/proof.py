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
  * A verifier may only rely on what survives redaction. Operator credentials
    are recorded as `Bearer <redacted>`, so "the two requests used different
    credentials" is not checkable from the artifacts and must not be a check -
    what is checkable is that both presented one, on the same endpoint, and
    one was refused.
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
# `machine\user` is also the shape of a path and of a sentence, so the shape
# alone cannot carry this check: the old pattern matched C:\Windows\System32
# and the words "domain\user" in prose, and its `\s*$` anchor denied a real
# Windows proof whenever the output was not at the end of a line. Strong forms
# only: a named service account anywhere, or a machine\user token alone on its
# own line - which is exactly what `whoami` prints.
# `nt authority\<service>` is unambiguous. A bare `machine\user` is not: it is
# also `docs\readme` and `bin\tool.exe`, and a page containing one of those on
# its own line graded rce when the request happened to carry a nonce. So the
# ambiguous form is accepted only out of a NON-HTML body - `whoami` output
# arrives as text or JSON from a diagnostic endpoint, while the false positive
# lives in incidental HTML content.
WINIDENT_RE = re.compile(
    r"(?i)(?:^|[^\w.:\\-])(nt authority\\{1,2}"
    r"(?:system|local service|network service|iusr))\b")
WINIDENT_WEAK_RE = re.compile(
    r"(?im)^\s*([a-z0-9][a-z0-9_-]{1,14}\\{1,2}[a-z0-9_.-]{1,20}\$?)\s*$")

# The marker this system sends. `probe_cmdi` builds it with _marker("argus"),
# and the matrix requires that prefix: accepting "any 6-32 char token present
# in both the request and the response" passed for free on every page that
# echoes a parameter, so `?host=aaaaaa` was a valid nonce.
NONCE_RE = re.compile(r"(?i)\bargus[a-z0-9]{4,24}\b")
# A deserialization payload carries its command inside a gadget, not after a
# shell separator - so `deserialize` inherited a declaration check it could
# never pass, and the class was unprovable by construction.
SERIALIZED_RE = re.compile(
    r"(?i)(!!python/(?:object|name)|!!ruby/object|cos\nsystem|c__builtin__"
    r"|__reduce__|cPickle|O:\d+:[\"']|a:\d+:\{|rO0AB|aced0005"
    r"|\$\$ND\b|ObjectDataProvider|BinaryFormatter|TypeConfuseDelegate"
    r"|__proto__\s*[\":]|constructor\s*\[\s*[\"']prototype"
    r"|yaml\.(?:unsafe_)?load\s*\()")

COMMAND_SENT_RE = re.compile(
    r"(?i)(?:[;|&\n]|\$\(|`|%0a|%3b|\|\|)\s*"
    r"(?:id|whoami|uname|hostname|pwd|ver|cat|echo)"
    r"(?=\s|;|\||&|$|\)|`|'|\")")

# The veto. It exists so a demonstration whose proof is the damage cannot be
# recorded, and the first version missed 21 of 24 payloads an auditor tried -
# a webshell drop, a reverse shell, crontab persistence, powershell, a piped
# curl. `passwd` is matched as a command (`passwd bob`), not as the path
# /etc/passwd, which is an ordinary read.
DESTRUCTIVE_RE = re.compile(
    r"(?i)("
    # destroy or truncate
    r"\brm\s+-[a-z]*[rf]|\bmkfs\b|\bdd\s+if=|\bshred\b|\btruncate\s+-s"
    r"|\b(shutdown|reboot|halt|poweroff|init\s+[06])\b"
    r"|\b:\s*\(\s*\)\s*\{|>\s*/dev/sd|\bwipefs\b"
    # persist or escalate
    r"|\b(useradd|adduser|usermod|groupadd)\b|\bpasswd\s+[a-z]"
    r"|net\s+user\s+\S+\s+/add|\bnet\s+localgroup\b"
    r"|\b(crontab|at\s+now|schtasks|systemctl\s+enable|launchctl\s+load"
    r"|reg\s+add)\b"
    r"|\bauthorized_keys\b|/etc/sudoers|\bvisudo\b|\bsetfacl\b|\bxattr\b"
    r"|\bchmod\s+[0-7]*[1357][0-7]*\s|\bchmod\s+[ugoa]*\+s\b|\bchown\s+root"
    r"|\bln\s+-s|\bmv\s+/|\bcp\s+/bin/|\binstall\s+-m\s*[0-7]*[1357]"
    # shell out
    r"|\bnc\s+-[a-z]*e|\b(ba|z|k)?sh\s+-i\b|/dev/tcp/|/dev/udp/"
    r"|\bsocat\b|\bmkfifo\b|\bpty\.spawn\b|\bbusybox\s+nc\b"
    r"|\btelnet\s+\d|\bssh\s+-R\b|\bchisel\b|\bligolo\b"
    # download-and-run, or run code
    r"|\b(curl|wget|fetch)\b[^|;&\n]*\|\s*(ba)?sh"
    r"|\b(curl\s+-[a-zA-Z]*o|wget\s+-[a-zA-Z]*O)\b"
    r"|\bcertutil\s+-urlcache|\binvoke-webrequest\b|\bbitsadmin\b"
    r"|\bbase64\s+-d[^|]*\|\s*(ba)?sh"
    r"|\b(python3?|perl|ruby|php|node|lua|osascript)\s+-[ecr]\b"
    r"|\bpowershell\b|\bpwsh\b|\bIEX\s*\(|\bFromBase64String\b"
    r"|\b(pip3?|npm|gem|apt-get|apt|yum|dnf|brew)\s+(install|i)\b"
    r"|\bdocker\s+(run|exec|cp)\b|\bkubectl\s+(exec|cp|apply)\b"
    r"|\baws\s+s3\s+(cp|sync|mv)\b|\bgcloud\s+storage\b|\bscp\b|\brsync\b"
    # write into anything served, or append to a config
    r"|>>?\s*\S*/(?:www|html|htdocs|webroot|public|wwwroot|cgi-bin)/"
    r"|\btee\s+(-a\s+)?\S*/(?:www|html|htdocs|public|etc)/"
    r"|>>\s*/etc/"
    r")")

# A query operator, not any key that starts with `$`: `{"$schema": ...}` and
# `{"$ref": ...}` are ordinary JSON and used to prove nosqli, while the
# bracketed urlencoded carrier `?user[$ne]=x` - which is how the carrier
# actually arrives - proved nothing.
# What a returned document looks like in a response, as opposed to a page that
# merely echoed the operator back. Any one of: a Mongo object id (the field or
# the 24-hex value), a BSON type marker, or a JSON array of objects. A page's
# own prose satisfies none of them, which is the whole point: `$ne` in the
# REQUEST proves a payload was sent, never that a store answered it.
RECORD_RE = re.compile(
    r"(?i)(\"_id\"\s*:"
    r"|ObjectId\(\s*[\"']?[0-9a-f]{24}"
    r"|\"\$oid\"\s*:"
    r"|\"\$numberLong\"\s*:"
    r"|\"\$date\"\s*:"
    r"|\[\s*\{[^{}]*\"[^\"]+\"\s*:)")

NOSQL_OP_RE = re.compile(
    r"(?i)("
    r"[\"']?\$(?:ne|gt|gte|lt|lte|regex|where|in|nin|exists|expr|function|or|and|not)"
    r"[\"']?\s*:"
    r"|\[\s*\$(?:ne|gt|gte|lt|lte|regex|where|in|nin|exists)\s*\]"
    r"|%5b%24(?:ne|gt|gte|lt|lte|regex|where|in|nin|exists)%5d"
    r")")

DBMS_RE = re.compile(
    r"(?i)("
    r"sqlite3?\.\w*error|sqlite_master|sqlite_version|sqlite version \d"
    r"|you have an error in your sql syntax|mysql_fetch|mysqli?_|mariadb"
    r"|\b\d+\.\d+\.\d+-\d*(?:mariadb|log|ubuntu|debian|mysql|azure|aws)"
    r"|psycopg2?|pg::|postgresql|postgres\s+\d|org\.postgresql|pg_catalog"
    r"|ORA-\d{5}|oracle database|pl/sql|v\$version"
    r"|microsoft (?:ole db|sql server)|sqlstate\[|sqlserverexception"
    r"|incorrect syntax near|unclosed quotation mark|\bsql server\s+\d{4}\b"
    r")")

# "the query named its target" has to mean the request carried SQL that names
# a table. The first version was `\b(?:from|join|into|update)\s+<ident>` over
# req_text - which unquote_plus-es the whole request - so `?q=mail+from+bob`
# became "mail from bob" and named the table `bob`. An ordinary search box
# satisfied the check, and sqli graded `proven` on a target with no injection
# in it. Measured against /search?q=mail+from+bob.
TABLE_RE = re.compile(
    r"(?i)(?:union[\s/*]+(?:all[\s/*]+)?select\b[\s\S]{0,400}?\bfrom\s+"
    r"[`\"\[]?([a-z_][a-z0-9_.]*)"
    r"|\bselect\b[\s\S]{0,400}?\bfrom\s+[`\"\[]?([a-z_][a-z0-9_.]*)"
    r"|\b(information_schema\.[a-z_]+|sqlite_master|pg_catalog\.[a-z_]+|"
    r"msysobjects|all_tables|user_tables|dba_tables)\b)")

# A file read asked for a file. Without this, any page quoting a passwd line -
# a security blog, this project's own README - graded as an arbitrary read.
TRAVERSAL_RE = re.compile(
    r"(?i)(\.\.[/\\]|%2e%2e|\.\.%2f|%252e"
    r"|/etc/(?:passwd|shadow|hosts|group|issue|hostname|fstab|crontab)"
    r"|/proc/(?:self|\d+)/|c:[/\\]{1,2}win|boot\.ini|win\.ini"
    r"|file://|php://|zip://|data://|expect://|/windows/win"
    r"|%00|\x00)")

# What makes data a SUBJECT rather than a page: an access-control claim needs
# the bytes to identify a person or an account, or `/page/1` vs `/page/2`
# grades as broken access control.
# JSON-quoted, or a form/query parameter. `<div role="navigation">` matched the
# bare `role=` form, which re-opened the pagination bypass on any HTML page.
SUBJECT_RE = re.compile(
    r"(?i)(?:\"(?:user_?name|login|e?-?mail|user_?id|uid|full_?name|"
    r"first_?name|last_?name|phone|mobile|ssn|dob|address|role|roles|"
    r"is_?admin|account_?(?:id|no|number)|customer_?id|owner|owner_?id|"
    r"tenant|card_?(?:number|no)|iban|balance)\"\s*:"
    r"|[?&](?:username|login|email|user_id|uid|account_id|customer_id|"
    r"owner|role)=)")

# A write the defence would have stopped carries one of these.
CSRF_TOKEN_RE = re.compile(
    r"(?i)(csrf[-_]?token|xsrf[-_]?token|authenticity_token|__requestverification"
    r"|x-csrf|anti[-_]?forgery|_token\b|state=)")

# Fields a caller should not be able to set on itself.
PRIVILEGED_FIELD_RE = re.compile(
    r"(?i)(?:\"(?:is_?admin|isadmin|admin|role|roles|permissions?|scopes?|"
    r"is_?staff|is_?superuser|verified|email_?verified|balance|credit|"
    r"price|discount|owner_?id|account_?type|plan|tier)\"\s*:"
    r"|[?&](?:is_admin|isAdmin|admin|role|permissions|scope|verified|"
    r"balance|price|discount|owner_id|account_type|plan|tier)=)")

# A placeholder is not a credential: `password=changeme` in an install
# document used to grade `disclosure` proven.
PLACEHOLDER_RE = re.compile(
    r"(?i)^(?:your|my|the)?[-_ ]?(?:x{3,}|\*{3,}|\.{3,}|<[^>]+>|\{\{?[^}]+\}?\}|"
    r"\$\{[^}]+\}|changeme|change_me|placeholder|example|examplekey|sample|"
    r"dummy|test|testing|secret|password|passwd|pass|hunter2|redacted|none|"
    r"null|nil|todo|tbd|insert[-_ ]?\w+[-_ ]?here|your[-_ ]?\w+[-_ ]?here|"
    r"api[-_ ]?key)[-_ ]?(?:here|value|goes[-_ ]?here)?$")

PASSWD_RE = re.compile(r"root:.?:0:0:")
WIN_INI_RE = re.compile(r"(?i)\[(fonts|extensions|mci extensions|boot loader)\]")
PRIVKEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----")
# A response that REFUSED the injection is not its data: `nosqli` graded
# `proven` on `{"error":"invalid operator"}` because the excerpt was in the
# response and nothing asked whether the response was a rejection.
REFUSAL_RE = re.compile(
    r"(?i)\b(error|errors|invalid|illegal|malformed|unsupported|not allowed|"
    r"not permitted|denied|forbidden|unauthorized|rejected|bad request|"
    r"disabled|unavailable|failed|failure)\b")

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

# An object reference is not always an integer. Matching only digits made
# idor unprovable on every API that uses uuids or opaque ids, which is most of
# them.
OBJECT_REF_RE = re.compile(
    r"(?i)(?:^|[/?&])(?:id|uid|user_?id|order|account|doc|object|num|pk|ref|"
    r"key|guid|uuid)=([\w.-]{1,64})"
    r"|/(\d{1,12}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"|[0-9a-f]{24,64})(?=/|$|\?)")


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


def _req(entry) -> dict:
    """This entry's request as a dict, or an empty one.

    `_req(entry)` reads as a guard and is not one: a LIST is
    truthy, so `.get` on it raises, and twelve classes' verifiers died that
    way on a malformed entry - reported by `grade()` as "evidence is
    readable" failing, which hides whatever the real answer was.
    """
    req = entry.get("request") if isinstance(entry, dict) else None
    return req if isinstance(req, dict) else {}


def _resp(entry) -> dict:
    resp = entry.get("response") if isinstance(entry, dict) else None
    return resp if isinstance(resp, dict) else {}


def req_text(entry: dict) -> str:
    req = _req(entry)
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


def _witness(candidates, build, required: tuple[str, ...]) -> list[dict]:
    """Grade against ONE witness, not against the union of the cited set.

    This is the fix for the deepest hole the matrix shipped with. `_grade`
    ANDs its checks, and every check used to scan the whole cited set
    independently - so an rce claim reached `proven` by citing a request that
    sent `id` and got nothing back, PLUS an unrelated debug page that happened
    to print `uid=33(www-data)`. Each check passed somewhere; nothing was
    executed anywhere. Measured, not imagined.

    A proof is an observation. The conjunction has to hold on one exchange, or
    on one correlated pair - so each candidate witness is scored on its own
    checks and the best-scoring one is reported. A class whose proof genuinely
    spans exchanges (a sentinel and its control, a dump and its fingerprint)
    passes those as separate checks, or passes a PAIR as the candidate.
    """
    best, best_score = None, -1
    for cand in candidates:
        checks = build(cand)
        passed = {c["check"] for c in checks if c["ok"]}
        score = sum(1 for name in required if name in passed)
        if score > best_score:
            best, best_score = checks, score
    return best if best is not None else build(None)


# How many cited exchanges take part in pairing. Beyond this the first N are
# used and the verdict records that the citation was truncated for grading.
_MAX_PAIRED = 16


def _pairs(exchanges: list[dict]) -> list:
    """Ordered pairs of distinct cited exchanges, for classes whose proof is a
    contrast. Ordered, because "A reached B's data" is not the same claim as
    "B reached A's".

    Each exchange also appears alone, as `(a, None)`. Without that a claim
    citing one exchange scored zero on every check and came back `unproven`
    with nothing to act on - the half of the requirement it DID meet has to
    still register, so the missing half can be named.
    """
    # Bounded: the pairing is O(N^2) and `_witness` runs the verifier on every
    # candidate, so a claim citing 200 exchanges was 40,000 verifier runs over
    # full response bodies. A contrast needs two exchanges, not two hundred;
    # the cap is generous and the verdict says when it bit.
    kept = exchanges[:_MAX_PAIRED]
    out = [(a, b) for a in kept for b in kept if a is not b]
    out += [(a, None) for a in kept]
    return out


_GRADE_RANK_ORDER = ("unproven", "candidate", "proven")


def _clamp(grade: str, ceiling: str) -> str:
    """Hold a grade at a class's ceiling.

    Some classes cannot be settled by anything this system observes: xss needs
    a browser, and seven classes were graded by "these two responses differ",
    which is true of any two pages on any site. Capping them at `candidate` and
    naming what a proof would need is the honest answer; letting them reach
    `proven` on a difference was not.
    """
    if not ceiling or grade in ("refused",):
        return grade
    try:
        return _GRADE_RANK_ORDER[min(_GRADE_RANK_ORDER.index(grade),
                                     _GRADE_RANK_ORDER.index(ceiling))]
    except ValueError:
        return grade


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

def _echo_check(claim: Claim, spec: "ProofSpec") -> dict:
    """The target produced the quoted bytes - the request did not.

    A precondition of EVERY class, and I implemented it twice as a per-class
    detail (lfi's sentinel, disclosure's secret) instead of once here. The cost
    was measured: one search box echoing its query graded `sqli` and `nosqli`
    **proven**, and lfi, xxe and massassign `candidate`, on a target with
    nothing behind it. Send `SELECT a,b FROM users -- admin - s3cr3t` and quote
    `admin - s3cr3t` out of the reflection.

    The exception is the classes whose artifact IS a reflection - xss, prototype
    pollution, crlf - which declare `reflection_is_the_finding`.
    """
    if spec.reflection_is_the_finding or not claim.excerpt:
        return _check("the target produced the quoted bytes", True, "")
    carrying = [e for e in claim.exchanges if claim.excerpt in resp_body(e)]
    produced = [e for e in carrying if claim.excerpt not in req_text(e)]
    ok = bool(produced)
    return _check(
        "the target produced the quoted bytes", ok,
        f"from {produced[0].get('id')}" if ok else
        ("every cited response carrying the quoted bytes was answering a "
         "request that already contained them - that is an echo, not a finding"
         if carrying else
         "the quoted bytes are in no cited response"))


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
    # The body is not the only channel. User enumeration and verb handling
    # often answer with identical bodies and different statuses, and reading
    # bodies alone made those differences invisible - `_discriminates` returned
    # "that is boilerplate" for a 200 against a 429.
    statuses = {status_of(e) for e in claim.exchanges}
    status_diff = len(claim.exchanges) >= 2 and len(statuses) > 1
    if ok:
        detail = f"present in {present[0]}, absent from {absent[0]}"
    elif status_diff:
        ok, detail = True, (f"identical bodies, statuses {sorted(statuses)} - "
                            "the difference is in the status line")
    elif len(bodies) < 2:
        detail = "only one exchange cited; a difference needs its control"
    else:
        detail = ("the excerpt is in every cited response and the statuses "
                  "match - that is boilerplate, not a difference")
    return _check(name, ok, detail)


ACL_HEADER_RE = re.compile(
    r"(?i)x-original-url|x-rewrite-url|x-forwarded-host|x-forwarded-for|"
    r"x-forwarded-server|x-host|x-custom-ip-authorization|x-remote-addr|"
    r"x-real-ip|x-originating-ip|x-client-ip")


def _req_headers(entry: dict) -> dict:
    headers = _req(entry).get("headers")
    return headers if isinstance(headers, dict) else {}


def _path_of(entry: dict) -> str:
    url = str(_req(entry).get("url") or "") if entry else ""
    return urllib.parse.urlparse(url).path or "/"


def _redirect_host(location: str) -> str:
    """The host a Location header actually sends the browser to, or "" when it
    stays on the current origin.

    `/home` is relative and therefore in-origin; an early version prefixed
    anything without "//" with it and read `/home` as the host `home`, so the
    in-origin control graded as the finding itself.
    """
    value = str(location or "").strip()
    if not value:
        return ""
    # `javascript:` and `data:` have no host, and returning "" read them as
    # in-origin - so a redirect to `javascript:alert(1)`, which the lab plants
    # and probe_redirect detects, graded `unproven`. They are the most
    # dangerous destination a Location can carry, not the safest.
    scheme = value.split(":", 1)[0].lower() if ":" in value else ""
    if scheme in ("javascript", "data", "vbscript", "file"):
        return f"{scheme}:"
    if value.startswith("//"):
        return urllib.parse.urlparse("http:" + value).hostname or ""
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme and parsed.netloc:
        return parsed.hostname or ""
    if parsed.scheme or value.startswith("/") or not parsed.netloc:
        return ""
    return urllib.parse.urlparse("http://" + value).hostname or ""


def _endpoint_shape(entry: dict) -> str:
    """The resource two exchanges have to share to be a pair: the path with
    its numeric segments collapsed, plus the sorted parameter names.

    `/api/user/1` and `/api/user/2` are one endpoint; `/api/user/1` and
    `/articles/2` are not, and comparing them as a pair is how pagination
    graded as broken access control.
    """
    url = str(_req(entry).get("url") or "")
    parsed = urllib.parse.urlparse(url)
    # The HOST is part of the endpoint. Dropping it made two tenants of a
    # multi-tenant app - alice.saas.test and bob.saas.test, each reading their
    # own record - compare as one endpoint, and two legitimate accounts graded
    # as broken access control.
    host = (parsed.hostname or "").lower()
    # an opaque id is an id: a uuid or a long slug segment collapses too, or
    # idor is unprovable on every API that does not use integers
    path = re.sub(r"/(?:\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-"
                  r"[0-9a-f]{12}|[0-9a-f]{24,64})(?=/|$)",
                  "/{id}", parsed.path or "/", flags=re.I)
    params = tuple(sorted(k for k, _ in urllib.parse.parse_qsl(parsed.query)))
    return host + path + ("?" + ",".join(params) if params else "")


def _credential(entry: dict) -> str:
    """The credential a request presented, as one comparable string. Empty when
    it presented none."""
    parts = []
    for key, value in _req_headers(entry).items():
        if str(key).lower() in ("authorization", "cookie", "x-api-key",
                                "x-auth-token", "api-key", "x-access-token"):
            parts.append(f"{str(key).lower()}={value}")
    return "|".join(sorted(parts))


def _object_refs(entry: dict) -> set[str]:
    url = str(_req(entry).get("url") or "")
    refs = set()
    for m in OBJECT_REF_RE.finditer(url):
        refs.add(m.group(1) or m.group(2))
    return {r for r in refs if r}


def _ceiling_reason(spec: "ProofSpec") -> str:
    """Why a class cannot be settled here, for the verdict to carry."""
    return (spec.notes or spec.requirement or
            "this system cannot settle this class")


# --- verifiers ---------------------------------------------------------------

def verify_command_output(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Code execution. One exchange has to carry the whole proof.

    The requirement is a single observation: a benign command went out and its
    output came back. Evaluating the three checks over the cited SET let a
    claim combine a request that sent `id` and got nothing with an unrelated
    debug page printing `uid=33(www-data)`, and grade `proven` with nothing
    executed. So each exchange is scored on its own, and the best one is
    reported.
    """
    destructive = [e.get("id") for e in claim.exchanges
                   if DESTRUCTIVE_RE.search(req_text(e))]

    def build(entry: dict | None) -> list[dict]:
        checks = []
        request = req_text(entry) if entry else ""
        body = resp_body(entry) if entry else ""
        rid = (entry or {}).get("id", "?")

        if spec.declares == "serialized":
            sent = bool(entry) and bool(SERIALIZED_RE.search(request))
            checks.append(_check(
                "a serialized payload was sent", sent,
                f"exchange {rid}" if sent else
                "no cited request carries a serialization gadget "
                "(!!python/object, O:n:\"...\", rO0AB, pickle opcodes)"
                if entry else "no exchange cited"))
        else:
            sent = bool(entry) and bool(COMMAND_SENT_RE.search(request))
            checks.append(_check(
                "a benign command was sent", sent,
                f"exchange {rid}" if sent else
                "no cited request carries a separator followed by a read-only "
                "command (id/whoami/uname/echo)" if entry else "no exchange cited"))

        html = bool(entry) and bool(re.search(
            r"(?i)text/html|application/xhtml",
            str((_resp(entry).get("headers")) or "")))
        hit = None
        if entry:
            hit = IDENTITY_RE.search(body) or WINIDENT_RE.search(body)
            if hit is None and not html:
                hit = WINIDENT_WEAK_RE.search(body)
        reflected = bool(hit) and hit.group(0).strip() in request
        checks.append(_check(
            "identity output returned by the target",
            bool(hit) and not reflected,
            f"{hit.group(0).strip()!r} in {rid}" if hit and not reflected else
            (f"the identity line in {rid} is also in its own request - that is "
             "a reflection, not execution" if reflected else
             "no uid=N(...) or whoami line in this response. Echoing `id` back "
             "as text does not produce one")))

        # The nonce this system sends, in the same exchange, both ways.
        nonce = None
        if entry:
            for token in NONCE_RE.findall(request):
                if token.lower() in body.lower():
                    nonce = token
                    break
        checks.append(_check(
            "the probe nonce came back in the output", nonce is not None,
            f"{nonce!r} in {rid}" if nonce else
            "this exchange did not send an argus<random> nonce and get it back. "
            "Send `id; echo <nonce>` so the output is tied to this probe - a "
            "token the page happens to echo is not a nonce"))

        checks.append(_check(
            "proof command stayed benign", not destructive,
            "" if not destructive else
            f"{destructive} sent more than a read - the evidence is void"))
        return checks

    return _witness(claim.exchanges or [None], build, spec.required)


def verify_data_extraction(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Injection into a data store: a named read, and its rows.

    The fingerprint may legitimately come from a different exchange than the
    dump - that is the documented workflow, one `@@version` read and then the
    extraction - so it stays a set-wide check. The other two must hold on ONE
    exchange: a request that names a table and a response that returns rows
    from it. Scoring them separately let a claim pair an unrelated SQL-shaped
    request with any row-looking text elsewhere.
    """
    checks = []
    if spec.fingerprint:
        banner = next((DBMS_RE.search(resp_text(e)) for e in claim.exchanges
                       if DBMS_RE.search(resp_text(e))), None)
        checks.append(_check("data store fingerprinted", banner is not None,
                             banner.group(0)[:80] if banner else
                             "no engine named in any cited response; read "
                             "@@version / version() / sqlite_version() once, or "
                             "cite the error that names it"))

    def build(entry: dict | None) -> list[dict]:
        out = []
        request = req_text(entry) if entry else ""
        body = resp_body(entry) if entry else ""
        rid = (entry or {}).get("id", "?")
        named = TABLE_RE.search(request) if entry else None
        if not named and entry and not spec.fingerprint:
            # a document store has no FROM clause: the operator injection is
            # what names the query as reaching the store
            named = NOSQL_OP_RE.search(request)
        out.append(_check(
            "the query named its target", named is not None,
            f"{(named.group(1) or named.group(2) or named.group(0)).strip()} "
            f"in {rid}" if named else
            ("no cited request carries an operator query ($ne, $regex, $where) "
             "or names a collection" if not spec.fingerprint else
             "no cited request carries SQL that names a table - a boolean "
             "differential proves the channel, not the read")))
        # A document store has no FROM clause, so the request cannot carry
        # evidence of a read - only of an attempt. The response has to. A
        # search box that reflects `{"$ne": null}` into its "no results"
        # message satisfied every check here before this: the operator was in
        # the request, the status was 200, and the body was not a DBMS error.
        # That graded `proven` on a page with no database behind it at all.
        records = RECORD_RE.search(body) if entry else None
        # a document shape the REQUEST also carries is the payload coming
        # back, not a record going out
        if records is not None and records.group(0) in request:
            records = None
        if not spec.fingerprint:
            out.append(_check(
                "documents came back, not the payload", records is not None,
                f"{records.group(0)[:60]} in {rid}" if records else
                "no cited response carries a document shape (_id, ObjectId, "
                "$oid, or a JSON array of objects) - an operator in the "
                "request proves a payload was sent, not that a store "
                "answered it"))
        quoted = bool(claim.excerpt) and claim.excerpt in body
        is_error = bool(claim.excerpt) and (
            bool(DBMS_RE.search(claim.excerpt))
            or bool(REFUSAL_RE.search(claim.excerpt)))
        answered = bool(entry) and status_of(entry) < 400
        enough = bool(named) and (spec.fingerprint or records is not None)
        out.append(_check(
            "rows returned, not an error message",
            enough and quoted and not is_error and answered,
            f"quoted from {rid}" if enough and quoted and not is_error
            and answered else
            ("the excerpt is an error or a refusal, not data" if is_error else
             f"{rid} answered {status_of(entry)} - the store refused the query"
             if enough and quoted and not answered else
             f"the quoted bytes are not in {rid}" if enough and not quoted else
             "the exchange the rows are quoted from returned no document "
             "shape" if named else
             "the exchange the rows are quoted from never named a table")))
        return out

    required = ["the query named its target",
                "rows returned, not an error message"]
    if not spec.fingerprint:
        required.insert(1, "documents came back, not the payload")
    checks += _witness(claim.exchanges or [None], build, tuple(required))
    rows = claim.excerpt.count("\n") + 1 if claim.excerpt else 0
    checks.append(_check("extraction stayed minimal", rows <= 20,
                         "" if rows <= 20 else
                         f"{rows} lines quoted - five rows is a proof, a dump "
                         "is an incident"))
    return checks


def verify_operator_injection(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """NoSQL operator injection: the operator CHANGED what the store answered.

    This used to share `verify_data_extraction` with sqli, and inherited its
    shape: "a document came back" plus "the request carried an operator".
    Both are true of any JSON API that was merely probed - `/api/posts`
    returns `[{"_id": ...}]` whether or not the `$ne` in the query did
    anything - so a PUBLIC listing graded `proven` the moment somebody
    pointed a probe at it. Found by an adversarial audit.

    A document store has no FROM clause, so the request can only ever show an
    attempt. The evidence has to be a DIFFERENCE against a control to the
    same endpoint without the operator, and it comes in two shapes, both of
    which `probe_nosqli` records:

    * **access** - the control was refused and the operator request was not.
      That is the authentication bypass, and it is the common real one.
    * **extraction** - the operator response carries documents the control's
      does not.

    Either way a control is required. Without one there is no way to tell an
    injection from an endpoint doing its job.
    """
    checks: list[dict] = []
    withop = [e for e in claim.exchanges if NOSQL_OP_RE.search(req_text(e))]
    checks.append(_check(
        "the request carried an operator query", bool(withop),
        f"{NOSQL_OP_RE.search(req_text(withop[0])).group(0)[:40]} in "
        f"{withop[0].get('id')}" if withop else
        "no cited request carries an operator query ($ne, $gt, $regex, "
        "$where) - without one nothing was injected"))

    def build(entry: dict | None) -> list[dict]:
        out = []
        rid = (entry or {}).get("id", "?")
        body = resp_body(entry) if entry else ""
        controls = [e for e in claim.exchanges
                    if entry is not None and e is not entry
                    and _endpoint_shape(e) == _endpoint_shape(entry)
                    and not NOSQL_OP_RE.search(req_text(e))] if entry else []
        refused_control = next(
            (c for c in controls if status_of(c) >= 400), None)
        answered = bool(entry) and 200 <= status_of(entry) < 300
        access = bool(refused_control and answered)
        records = RECORD_RE.search(body) if entry else None
        if records is not None and entry is not None and \
                records.group(0) in req_text(entry):
            records = None
        extraction = bool(records) and any(
            not RECORD_RE.search(resp_body(c)) for c in controls)
        changed = access or extraction
        if changed:
            detail = (f"{refused_control.get('id')} was refused "
                      f"{status_of(refused_control)} and {rid} answered "
                      f"{status_of(entry)}" if access else
                      f"{records.group(0)[:40]} in {rid} and in no control")
        elif not controls:
            detail = ("no control cited: a request to the same endpoint "
                      "WITHOUT the operator is what separates an injection "
                      "from an endpoint doing its job")
        elif records is not None:
            detail = (f"{controls[0].get('id')} returns documents too - that "
                      "is what this endpoint answers anyway")
        else:
            detail = (f"{rid} answered {status_of(entry)} and no control was "
                      "refused, and no document shape came back that a "
                      "control lacks - the operator changed nothing")
        out.append(_check("the operator changed what the store answered",
                          changed, detail))
        quoted = bool(claim.excerpt) and claim.excerpt in body
        is_error = bool(claim.excerpt) and (
            bool(DBMS_RE.search(claim.excerpt))
            or bool(REFUSAL_RE.search(claim.excerpt)))
        ok = changed and quoted and not is_error
        out.append(_check(
            "the quoted bytes are the access, not an error", ok,
            f"quoted from {rid}" if ok else
            ("the excerpt is an error or a refusal, not the access gained"
             if is_error else f"the quoted bytes are not in {rid}"
             if changed and not quoted else
             "nothing changed to quote")))
        return out

    checks += _witness(claim.exchanges or [None], build,
                       ("the operator changed what the store answered",
                        "the quoted bytes are the access, not an error"))
    rows = claim.excerpt.count("\n") + 1 if claim.excerpt else 0
    checks.append(_check("extraction stayed minimal", rows <= 20,
                         "" if rows <= 20 else
                         f"{rows} lines quoted - five rows is a proof, a dump "
                         "is an incident"))
    return checks


def verify_file_read(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Arbitrary read: a sentinel out of a file, from a request that asked for
    one, plus a control path that does not exist.

    The first version never looked at the request, so a documentation page
    quoting `root:x:0:0` - or a security blog, or this project's own README -
    graded `candidate` for lfi. The sentinel also has to be absent from the
    request, or an attacker who posts the passwd line gets it echoed back.
    """
    control = None
    for entry in claim.exchanges:
        body = resp_body(entry)
        if not any(pat.search(body) for _, pat in FILE_SENTINELS) \
                and TRAVERSAL_RE.search(req_text(entry)):
            control = control or entry

    def build(entry: dict | None) -> list[dict]:
        out = []
        request = req_text(entry) if entry else ""
        body = resp_body(entry) if entry else ""
        rid = (entry or {}).get("id", "?")
        asked = bool(entry) and bool(TRAVERSAL_RE.search(request))
        hit = None
        for label, pattern in FILE_SENTINELS:
            m = pattern.search(body) if entry else None
            if m and m.group(0) not in request:
                hit = (label, m)
                break
        out.append(_check(
            "the request asked for a file", asked,
            f"exchange {rid}" if asked else
            "no traversal, absolute path or file:// wrapper in this request - "
            "a page that merely contains a passwd line is not a file read"))
        out.append(_check(
            "known-file sentinel observed", hit is not None,
            f"{hit[0]} in {rid}" if hit else
            "no /etc/passwd, win.ini or private-key signature in this response "
            "that was not already in its own request"))
        out.append(_check(
            "negative control recorded", control is not None,
            f"exchange {control.get('id')}" if control else
            "cite a request for a path that does not exist, so the sentinel is "
            "shown to come from the file and not from the page"))
        return out

    return _witness(claim.exchanges or [None], build, spec.required)


def verify_template_eval(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Server-side template injection: an arithmetic result the engine
    computed, plus a second operand pair that confirms it.

    One pair is not enough, and that was the hole: `{{2*2}}` plus any page
    containing the digit 4 - "Showing 4 results" - graded proven. A product is
    only evidence when a DIFFERENT pair produces ITS product too, because no
    page contains both by accident.
    """
    seen = []          # (literal, product, entry)
    echoed = None
    for entry in claim.exchanges:
        m = TEMPLATE_MATH_RE.search(req_text(entry))
        if not m:
            continue
        left, op, right = int(m.group(2)), m.group(3), int(m.group(4))
        product = str(left * right if op == "*" else left + right)
        body = resp_body(entry)
        if m.group(0) in body:
            echoed = entry
        elif product in body and product not in (str(left), str(right)):
            seen.append((m.group(0), product, entry, (left, op, right)))
    first = seen[0] if seen else None
    second = next((row for row in seen[1:]
                   if row[3] != first[3] and row[1] != first[1]), None) \
        if first else None
    return [
        _check(
            "expression evaluated, not echoed", first is not None,
            f"{first[0]} rendered as {first[1]} in {first[2].get('id')}"
            if first else
            (f"{echoed.get('id')} returned the expression unchanged - that is "
             "reflection" if echoed else
             "no cited request carries an arithmetic template expression "
             "({{7*7}}); a payload that is merely reflected proves nothing")),
        _check(
            "a second operand pair confirms it", second is not None,
            f"{second[0]} rendered as {second[1]} in {second[2].get('id')}"
            if second else
            "send a different pair - {{3*7}} after {{7*7}} - and cite it. One "
            "product can be a coincidence in the page; two cannot"),
    ]


def verify_differential(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Object-level access control: one actor reaching another's subject.

    Neighbouring ids returning different content is pagination as often as it
    is a bug - `/page/1` and `/page/2` graded proven. Two things make it this
    class: the data has to identify a SUBJECT, and the caller has to have been
    unentitled to it - either the two requests presented different credentials
    for the same resource, or no credential was presented at all and subject
    data came back anyway.
    """
    def build(pair) -> list[dict]:
        out = []
        if pair is None:
            mine = theirs = None
        else:
            mine, theirs = pair
        refs_a = _object_refs(mine) if mine else set()
        refs_b = _object_refs(theirs) if theirs else set()
        distinct = bool(refs_a and refs_b and refs_a != refs_b)
        same_shape = bool(mine) and bool(theirs) and \
            _endpoint_shape(mine) == _endpoint_shape(theirs)
        out.append(_check(
            "two distinct object references on one endpoint",
            distinct and same_shape,
            f"{sorted(refs_a)} vs {sorted(refs_b)} on {_endpoint_shape(theirs)}"
            if distinct and same_shape else
            ("the two cited requests are on different endpoints - cite the same "
             "endpoint with two ids" if distinct else
             "the cited requests do not carry two different object references")))
        body_b = resp_body(theirs) if theirs else ""
        body_a = resp_body(mine) if mine else ""
        quoted = bool(claim.excerpt) and claim.excerpt in body_b \
            and claim.excerpt not in body_a
        out.append(_check(
            "another subject's data returned", quoted,
            f"present in {theirs.get('id')}, absent from {mine.get('id')}"
            if quoted and theirs and mine else
            "the quoted bytes are in both cited responses, or in neither - that "
            "is boilerplate, not another subject"))
        subject = bool(claim.excerpt) and bool(SUBJECT_RE.search(claim.excerpt))
        out.append(_check(
            "the data identifies a subject", subject,
            "" if subject else
            "the quoted bytes name no subject field (username, email, role, "
            "owner, account id) - differing page content is not an access-"
            "control finding"))
        cred_a = _credential(mine) if mine else ""
        cred_b = _credential(theirs) if theirs else ""
        unentitled = bool(theirs) and (not cred_b or (cred_a and cred_a != cred_b))
        out.append(_check(
            "the caller was not entitled to it", unentitled,
            ("no credential was presented and subject data came back"
             if theirs is not None and not cred_b else
             "the two requests presented different credentials")
            if unentitled else
            "both requests carried the same credential, so this may be the "
            "caller's own data. Re-read it as another identity, or with none"))
        return out

    return _witness(_pairs(claim.exchanges) or [None], build, spec.required)


def verify_token_forgery(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A forged or absent credential accepted where a wrong one is refused.

    "Any 2xx whose headers mention a cookie, plus any 401 anywhere" is not that
    claim - every browser-shaped request carries a Cookie, and every site has a
    401 somewhere. The pair has to be the same endpoint with DIFFERENT
    credentials, one accepted and one refused.
    """
    # The mint, from the non-HTTP events the claim also cites. A working
    # authorisation check has the same shape on the wire as a forgery - a good
    # credential accepted, another refused - so what separates them is that
    # this system minted the one that was accepted. `jwt_forge` records it.
    minted = next((e for e in claim.events
                   if (e.get("kind") or "") == "jwt_forge"), None)
    claims_set = (minted or {}).get("claims_set")
    claims_set = claims_set if isinstance(claims_set, dict) else {}

    def build(pair) -> list[dict]:
        accepted, rejected = (pair if pair else (None, None))
        same = bool(accepted) and bool(rejected) and \
            _endpoint_shape(accepted) == _endpoint_shape(rejected)
        cred_a = _credential(accepted) if accepted else ""
        cred_r = _credential(rejected) if rejected else ""
        ok_code = bool(accepted) and 200 <= status_of(accepted) < 300
        deny = bool(rejected) and status_of(rejected) in (401, 403)
        # NOT "the credentials differ": GuardedClient redacts auth headers at
        # record time, so both exchanges persist as `Bearer <redacted>` and the
        # values are identical in every artifact. A verifier may only rely on
        # what survives redaction - what it can check is that the control
        # presented a credential too, on the same endpoint, and was refused.
        differ = bool(cred_r)
        quoted = bool(claim.excerpt) and bool(accepted) \
            and claim.excerpt in resp_body(accepted)
        echoed = [str(v) for v in claims_set.values()
                  if str(v) and accepted
                  and str(v) in resp_body(accepted)]
        return [
            _check("this system minted the credential",
                   minted is not None and bool(echoed),
                   f"jwt_forge {minted.get('id')} set "
                   f"{sorted(claims_set)}, echoed {echoed[0]!r}"
                   if minted is not None and echoed else
                   ("cite the jwt_forge event: nothing in the session shows the "
                    "accepted credential was minted here, and a working auth "
                    "check looks the same on the wire" if minted is None else
                    "none of the forged claims come back in the accepted "
                    "response - the server did not honour them")),
            _check("a forged credential was accepted",
                   ok_code and bool(cred_a) and quoted,
                   f"{_endpoint_shape(accepted)} returned "
                   f"{status_of(accepted)} with a credential"
                   if ok_code and cred_a and quoted else
                   "no cited exchange presents a credential, gets a 2xx and "
                   "carries the quoted bytes"),
            _check("the same endpoint refuses another credential",
                   same and deny and differ,
                   f"{_endpoint_shape(rejected)} answered "
                   f"{status_of(rejected)} to a credentialed request"
                   if same and deny and differ else
                   ("the refusal is on a different endpoint - cite the SAME "
                    "request with a broken signature" if deny and not same else
                    "cite the control: the same endpoint must refuse a "
                    "credential it does not accept. An anonymous 401 shows only "
                    "that auth is required, which is a different finding")),
        ]

    return _witness(_pairs(claim.exchanges) or [None], build, spec.required)


def verify_off_origin_redirect(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A 3xx Location off origin, carrying a destination the request supplied.

    An apex-to-www redirect is off origin too, and used to grade as the
    finding. What makes it open redirect is that the destination came from the
    request.
    """
    def build(pair) -> list[dict]:
        off, control = (pair if pair else (None, None))
        loc = header_of(off, "Location") if off else ""
        host = _redirect_host(loc)
        req_host = (urllib.parse.urlparse(
            str(_req(off).get("url") or "")).hostname or "") \
            if off else ""
        foreign = bool(host) and host.lower() != req_host.lower()
        supplied = foreign and host.lower() in req_text(off).lower()
        c_loc = header_of(control, "Location") if control else ""
        c_host = _redirect_host(c_loc)
        in_origin = bool(control) and bool(c_loc) and (
            not c_host or c_host.lower() == (urllib.parse.urlparse(
                str(_req(control).get("url") or "")
            ).hostname or "").lower())
        return [
            _check("the Location points off origin, to a host we supplied",
                   supplied,
                   f"{loc[:120]} in {off.get('id')}" if supplied else
                   (f"{loc[:80]} leaves the origin but that host is not in the "
                    "request - an apex-to-www hop is not an open redirect"
                    if foreign else
                    "no cited response carries a Location header leaving the "
                    "origin")),
            _check("control recorded for the expected outcome", in_origin,
                   f"exchange {control.get('id')}" if in_origin else
                   "cite the in-origin case too, so the parameter is shown to "
                   "be honoured rather than ignored"),
        ]

    return _witness(_pairs(claim.exchanges) or [None], build, spec.required)


def verify_unkeyed_input(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Cache poisoning / deception: a value one requester sent, served to a
    requester that did not send it, on the same resource.

    Without the same-resource condition a reflected search term that also
    appears somewhere else on the site graded as poisoning.
    """
    def build(pair) -> list[dict]:
        poisoner, victim = (pair if pair else (None, None))
        sent = bool(poisoner) and bool(claim.excerpt) \
            and claim.excerpt in req_text(poisoner)
        served = bool(victim) and bool(claim.excerpt) \
            and claim.excerpt in resp_body(victim) \
            and claim.excerpt not in req_text(victim)
        same = bool(poisoner) and bool(victim) and \
            _endpoint_shape(poisoner) == _endpoint_shape(victim)
        return [
            _check("the value reached a requester that did not send it",
                   sent and served and same,
                   f"sent in {poisoner.get('id')}, served to {victim.get('id')} "
                   f"on {_endpoint_shape(victim)}" if sent and served and same
                   else ("the two exchanges are on different resources - a value "
                         "appearing elsewhere on the site is not a cache entry"
                         if sent and served else
                         "no cited pair has one request sending the value and "
                         "another response returning it")),
            _check("the injecting request is on record", sent,
                   f"exchange {poisoner.get('id')}" if sent else
                   "cite the poisoning request as well as the victim read"),
        ]

    return _witness(_pairs(claim.exchanges) or [None], build, spec.required)


def verify_restricted_access(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Header-based access-control bypass: restricted content returned when an
    ACL-relevant header is added, refused on the same path without it.

    The refusal has to be a refusal. The first version accepted an ordinary
    2xx as the control, so any in-scope page could stand in for the denial.
    """
    def build(pair) -> list[dict]:
        served, refused = (pair if pair else (None, None))
        hdrs = " ".join(f"{k}: {v}" for k, v in _req_headers(served).items()) \
            if served else ""
        spoofed = bool(ACL_HEADER_RE.search(hdrs))
        quoted = bool(claim.excerpt) and bool(served) \
            and claim.excerpt in resp_body(served)
        got = bool(served) and spoofed and 200 <= status_of(served) < 300 and quoted
        r_hdrs = " ".join(f"{k}: {v}" for k, v in _req_headers(refused).items()) \
            if refused else ""
        denied = bool(refused) and status_of(refused) in (401, 403, 404) \
            and not ACL_HEADER_RE.search(r_hdrs)
        same = bool(served) and bool(refused) and \
            _path_of(served) == _path_of(refused)
        return [
            _check("restricted content returned with the header", got,
                   f"{status_of(served)} on {_path_of(served)} in "
                   f"{served.get('id')}" if got else
                   "no cited exchange adds an ACL-relevant header "
                   "(X-Original-URL, X-Forwarded-Host, X-Real-IP, ...), gets a "
                   "2xx, and carries the quoted bytes"),
            _check("the same request is refused without it", denied and same,
                   f"{_path_of(refused)} answered {status_of(refused)} in "
                   f"{refused.get('id')}" if denied and same else
                   ("the refusal is on a different path than the bypass - cite "
                    "the refusal of this path itself" if denied else
                    "cite the control: the same path without the header must "
                    "answer 401/403/404, or the resource was never restricted")),
        ]

    return _witness(_pairs(claim.exchanges) or [None], build, spec.required)


def verify_cors(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A foreign origin reflected into Access-Control-Allow-Origin, with
    credentials allowed. A correct allowlist echoing the site's own origin is
    not a finding, and used to grade as one.
    """
    def build(entry: dict | None) -> list[dict]:
        allow = header_of(entry, "Access-Control-Allow-Origin") if entry else ""
        origin = ""
        for k, v in _req_headers(entry).items() if entry else ():
            if str(k).lower() == "origin":
                origin = str(v)
        host = (urllib.parse.urlparse(
            str(_req(entry).get("url") or "")).hostname or "") \
            if entry else ""
        o_host = urllib.parse.urlparse(origin).hostname or "" if origin else ""
        foreign = bool(o_host) and o_host.lower() != host.lower()
        reflects = bool(allow) and bool(origin) and allow.strip() == origin.strip()
        creds = header_of(entry, "Access-Control-Allow-Credentials") \
            .strip().lower() == "true" if entry else False
        return [
            _check("a foreign probe origin is reflected", reflects and foreign,
                   f"{origin} echoed in {entry.get('id')}"
                   if reflects and foreign else
                   ("the reflected origin is the site's own - that is an "
                    "allowlist working" if reflects else
                    "no cited response echoes the Origin it was sent")),
            _check("credentials are allowed with it", creds,
                   f"exchange {entry.get('id')}" if creds else
                   "without Access-Control-Allow-Credentials: true a reflected "
                   "origin reads nothing authenticated - rate it info"),
        ]

    return _witness(claim.exchanges or [None], build, spec.required)


def verify_state_change(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A cross-origin write that no token protected, read back afterwards.

    "Any GET plus any POST plus any difference" is not CSRF - it is a web site.
    The write has to carry no anti-CSRF token and a foreign Origin/Referer.
    """
    reads = [e for e in claim.exchanges
             if str(_req(e).get("method") or "GET").upper()
             == "GET"]

    def build(entry: dict | None) -> list[dict]:
        method = str(_req(entry).get("method") or "GET").upper() \
            if entry else "GET"
        write = method in ("POST", "PUT", "PATCH", "DELETE")
        request = req_text(entry) if entry else ""
        tokened = bool(CSRF_TOKEN_RE.search(request))
        origin = ""
        for k, v in _req_headers(entry).items() if entry else ():
            if str(k).lower() in ("origin", "referer"):
                origin = str(v)
        host = (urllib.parse.urlparse(
            str(_req(entry).get("url") or "")).hostname or "") \
            if entry else ""
        o_host = urllib.parse.urlparse(origin).hostname or "" if origin else ""
        cross = bool(o_host) and o_host.lower() != host.lower()
        after = [e for e in reads
                 if bool(claim.excerpt) and claim.excerpt in resp_body(e)]
        before = [e for e in reads
                  if not claim.excerpt or claim.excerpt not in resp_body(e)]
        landed = bool(entry) and 200 <= status_of(entry) < 400
        return [
            _check("the state-changing request succeeded", write and landed,
                   f"{method} returned {status_of(entry)}"
                   if write and landed else
                   (f"the write was refused with {status_of(entry)} - that is "
                    "the defence working, not a finding" if write else
                    "no cited request changes state")),
            _check("the state-changing request carried no anti-CSRF token",
                   write and not tokened,
                   f"{method} {_endpoint_shape(entry)}" if write and not tokened
                   else ("the write carries a CSRF token - that is the defence "
                         "working" if write else "no cited request changes state")),
            _check("it was sent cross-origin", cross,
                   f"Origin/Referer {origin}" if cross else
                   "the write carries no foreign Origin or Referer, so nothing "
                   "shows a third-party site could have sent it"),
            _check("the state changed between two reads",
                   bool(after) and bool(before),
                   f"absent in {before[0].get('id')}, present in "
                   f"{after[0].get('id')}" if after and before else
                   "cite the read before and the read after; the quoted bytes "
                   "must appear only in the second"),
        ]

    return _witness(claim.exchanges or [None], build, spec.required)


def verify_secret_leak(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A credential observed in a response. A placeholder is not a credential,
    and an install document full of `password=changeme` used to grade proven.
    """
    hit = SECRET_RE.search(claim.excerpt or "")
    placeholder = ""
    if hit:
        value = re.split(r"[:=]", hit.group(0), maxsplit=1)
        if len(value) > 1 and PLACEHOLDER_RE.match(value[1].strip().strip("\"'")):
            placeholder = value[1].strip()
    # ...and not bytes the claimant sent themselves. A search box echoing
    # `?q=SECRET_KEY=lab-secret-0123` graded disclosure proven; the same trap
    # the lfi sentinel check already guards against.
    in_response = [e.get("id") for e in claim.exchanges
                   if claim.excerpt and claim.excerpt in resp_body(e)
                   and claim.excerpt not in req_text(e)]
    reflected = bool(claim.excerpt) and any(
        claim.excerpt in resp_body(e) and claim.excerpt in req_text(e)
        for e in claim.exchanges) and not in_response
    return [
        _check("a credential-shaped secret was observed",
               hit is not None and not placeholder,
               hit.group(0)[:24] + "..." if hit and not placeholder else
               (f"{placeholder!r} is a placeholder, not a credential"
                if placeholder else
                "the quoted bytes do not look like a credential; quote the key, "
                "token or key-value line itself")),
        _check("it came from a response, not from the request", bool(in_response),
               f"in {in_response[0]}" if in_response else
               ("the quoted bytes are in the request that produced them - the "
                "page echoed what you sent" if reflected else
                "the quoted bytes are in no cited response")),
    ]


def verify_browser_execution(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Reflection is checkable from the bytes; execution is not.

    The signal is a metacharacter surviving unencoded into an HTML response -
    not the presence of a `<script>` tag nearby, which an early version looked
    for and which failed the lab's own `<>'"&=/` canary.
    """
    reflected, encoded = None, None
    raw = [ch for ch in "<>\"'" if ch in (claim.excerpt or "")]
    for entry in claim.exchanges:
        body = resp_body(entry)
        if not claim.excerpt or claim.excerpt not in body:
            continue
        if not re.search(r"(?i)text/html|application/xhtml",
                         str((_resp(entry).get("headers")) or "")):
            continue
        if raw:
            reflected = (entry, "".join(raw))
        elif re.search(r"&lt;|&gt;|&quot;|&#x?\d", body):
            encoded = entry
    return [
        _check("payload reflected unencoded into HTML", reflected is not None,
               f"{reflected[1]!r} survived into {reflected[0].get('id')}"
               if reflected
               else ("the response entity-encodes the payload - that is the fix "
                     f"working ({encoded.get('id')})" if encoded else
                     "the quoted bytes carry no raw < > \" ' and so cannot break "
                     "out of their context, or they are in no cited HTML "
                     "response")),
        _check("a real browser executed it", False,
               "this system has no browser, so execution is not provable here. "
               "Drive one over mcp_call and cite the nonce it reports, or leave "
               "this a candidate and say so in the report"),
    ]


def verify_mass_assignment(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A privileged field the caller sent, set on the server and read back.

    This was graded by the idor verifier, which asks about object references
    and knows nothing about fields.
    """
    def build(pair) -> list[dict]:
        wrote, read = (pair if pair else (None, None))
        request = req_text(wrote) if wrote else ""
        field = PRIVILEGED_FIELD_RE.search(request) if wrote else None
        method = str(_req(wrote).get("method") or "GET").upper() \
            if wrote else "GET"
        sent = bool(field) and method in ("POST", "PUT", "PATCH") \
            and 200 <= status_of(wrote) < 400
        back = bool(read) and bool(claim.excerpt) \
            and claim.excerpt in resp_body(read) \
            and claim.excerpt not in req_text(read)
        return [
            _check("a privileged field was sent and accepted", sent,
                   f"{field.group(0)} in {wrote.get('id')}, "
                   f"{status_of(wrote)}" if sent else
                   (f"the write was refused with {status_of(wrote)}"
                    if wrote is not None and field else
                    "no cited write carries a field the caller should not be "
                    "able to set (role, is_admin, isAdmin, balance, verified, "
                    "owner, permissions)")),
            _check("a later read shows it set", back,
                   f"read back in {read.get('id')}" if back else
                   "cite the read that shows the field took effect - the write "
                   "echoing its own input proves only that it was accepted"),
        ]

    return _witness(_pairs(claim.exchanges) or [None], build, spec.required)


def verify_graphql(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Introspection answered, or a query returning records outside scope.

    This class was graded by the extraction verifier, which wants a FROM
    clause or a Mongo operator - neither of which a GraphQL query ever sends,
    so the class was unprovable by construction.
    """
    def build(entry: dict | None) -> list[dict]:
        request = req_text(entry) if entry else ""
        body = resp_body(entry) if entry else ""
        rid = (entry or {}).get("id", "?")
        asked = bool(entry) and bool(
            re.search(r"(?i)__schema|__type|\bquery\s*\{|\bmutation\s*\{", request))
        answered = bool(entry) and status_of(entry) < 400
        # an `errors` array with no `data` is the endpoint declining, and a
        # 404 plus "introspection is disabled" used to grade `proven`
        declined = bool(re.search(r'(?i)"errors"\s*:\s*\[', body)) and not \
            re.search(r'(?i)"data"\s*:\s*[\[{]\s*[^\s\]}]', body)
        introspected = asked and answered and not declined and bool(
            re.search(r'(?i)"__schema"|"types"\s*:\s*\[|"queryType"', body))
        records = asked and answered and not declined and bool(claim.excerpt) \
            and claim.excerpt in body and claim.excerpt not in request
        return [
            _check("a GraphQL query was sent", asked,
                   f"exchange {rid}" if asked else
                   "no cited request carries a GraphQL query, mutation or "
                   "introspection selection"),
            _check("the endpoint answered with schema or records",
                   introspected or records,
                   ("introspection answered" if introspected else
                    f"records quoted from {rid}") if introspected or records else
                   (f"{rid} answered {status_of(entry)}" if entry is not None
                    and not answered else
                    "the response is an `errors` array with no data - the "
                    "endpoint declined" if declined else
                    "the response carries neither the schema nor the quoted "
                    "records")),
        ]

    return _witness(claim.exchanges or [None], build, spec.required)


def verify_oracle(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """User enumeration: the same request telling a real account from an
    absent one, with both answers on record and the difference repeated.

    `_discriminates` asked only that two responses differ, which is true of
    any two pages - so this was capped at `candidate` with "one difference is
    not a counted series" as the reason. The series IS in the transcript: the
    probe sends a known and an unknown account, more than once.
    """
    by_shape: dict[str, list[dict]] = {}
    for entry in claim.exchanges:
        by_shape.setdefault(_endpoint_shape(entry), []).append(entry)
    series, shape = [], ""
    for key, rows in by_shape.items():
        if len(rows) > len(series):
            series, shape = rows, key
    # group the answers: body+status is the observable
    answers: dict[tuple, list[dict]] = {}
    for entry in series:
        answers.setdefault((resp_body(entry), status_of(entry)), []).append(entry)
    distinct = len(answers) >= 2
    repeated = distinct and all(len(v) >= 2 for v in
                                sorted(answers.values(), key=len,
                                       reverse=True)[:2])
    return [
        _check("the same request gave two different answers", distinct,
               f"{len(answers)} distinct answers over {len(series)} requests "
               f"on {shape}" if distinct else
               f"all {len(series)} cited requests on one endpoint answered "
               "alike - there is no oracle here"),
        _check("each answer was observed more than once", repeated,
               "both answers repeat" if repeated else
               "send each case twice: one differing response is noise until it "
               "repeats, which is why this needs a series and not a pair"),
    ]


# A credential field, which is what makes a request an authentication
# ATTEMPT rather than a page view. Checked on the request, because a lockout
# policy is about what the caller tried, not about what the page looks like.
_CREDENTIAL_FIELD_RE = re.compile(
    r"(?i)(?:^|[?&{\"'\s,])(?:password|passwd|pwd|pass|otp|passcode|"
    r"secret|pin|mfa|totp)(?:[\"']?\s*[=:])")
_AUTH_FAIL_RE = re.compile(
    r"(?i)invalid|incorrect|failed|denied|unauthori[sz]ed|bad credentials|"
    r"wrong (?:password|user)|\"ok\"\s*:\s*false")


def _is_auth_attempt(entry: dict) -> bool:
    return bool(_CREDENTIAL_FIELD_RE.search(req_text(entry)))


def _auth_failed(entry: dict) -> bool:
    """Did this attempt fail? A lockout policy governs failures."""
    if status_of(entry) in (401, 403):
        return True
    if 200 <= status_of(entry) < 300:
        return bool(_AUTH_FAIL_RE.search(resp_body(entry)))
    return status_of(entry) in (400, 422)


def verify_no_throttle(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """No lockout: a counted series of failed attempts, none of them refused.

    This class was graded by `_discriminates`, which asks for a DIFFERENCE
    between two responses - and the bug is characterised by the absence of
    one. So the real bug (every attempt answers 401 alike) graded `unproven`
    while the defence working (the sixth attempt answers 429) graded
    `candidate`. The requirement was backwards, and the `candidate` cap hid
    it: a cap that is really a missing implementation reads as a limit.
    """
    by_endpoint: dict[str, list[dict]] = {}
    for entry in claim.exchanges:
        if not _is_auth_attempt(entry):
            continue
        by_endpoint.setdefault(_endpoint_shape(entry), []).append(entry)
    series, shape = [], ""
    for key, rows in by_endpoint.items():
        if len(rows) > len(series):
            series, shape = rows, key
    throttled = [e for e in series
                 if status_of(e) == 429
                 or re.search(r"(?i)too many|rate limit|locked|try again later|"
                              r"temporarily (?:blocked|disabled)", resp_body(e))]
    failed = [e for e in series if _auth_failed(e)]
    enough = len(series) >= 5 and len(failed) >= 5
    if enough:
        why = f"{len(failed)} failed authentication attempts on {shape}"
    elif not series:
        why = ("no cited request carries a credential field (password, pass, "
               "pwd, otp, passcode) - five page views are not five "
               "authentication attempts, and this check used to accept them")
    elif len(series) < 5:
        why = (f"only {len(series)} authentication attempt(s) on one "
               "endpoint - send at least five, so 'never refused' means "
               "something")
    else:
        why = (f"{len(series)} attempts but only {len(failed)} failed - a "
               "lockout policy applies to FAILURES, so a series that "
               "succeeded says nothing about one")
    return [
        _check("a counted series of failed authentication attempts is on "
               "record", enough, why),
        _check("none of them was refused", enough and not throttled,
               f"all {len(series)} answered without a throttle" if enough
               and not throttled else
               (f"{throttled[0].get('id')} answered "
                f"{status_of(throttled[0])} - that is the lockout working"
                if throttled else "no series to judge")),
    ]


# A header name the probe put there. Deliberately narrow: an injected header
# whose name is one the server might legitimately send proves nothing, because
# you cannot tell who wrote it.
_CRLF_SEQ_RE = re.compile(r"(?i)(?:%0d%0a|%0a|\\r\\n|\r\n|%5cr%5cn|\\u000d\\u000a)")
_HEADER_SET_RE = re.compile(
    r"(?i)(?:%0d%0a|%0a|\\r\\n|\r\n)\s*([a-z0-9][a-z0-9-]{2,40})\s*(?::|%3a)\s*"
    r"([^\r\n&%]{1,120})")


def verify_header_injection(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """CRLF injection: a header the REQUEST asked for, present as a header.

    This class was capped at `candidate` with the note "this system compares
    bodies, so it stops at a candidate". That was true of `verify_generic`,
    and it was the wrong place to stop: the transcript records response
    headers as a dict, so the actual proof - a header that exists because the
    request asked for it - is checkable here.

    Three things have to hold on ONE exchange, which is why they are scored
    together as a witness rather than separately:

    1. the request carried a CRLF sequence followed by `name: value`;
    2. the response carries that header, with that value;
    3. a control exchange to the same endpoint does NOT carry it.

    (3) is what makes it a proof rather than a coincidence. A server that
    always sends `X-Cache: MISS` would otherwise satisfy (2) for a payload
    that happened to name `X-Cache`.
    """
    def build(pair) -> list[dict]:
        entry, control = pair if isinstance(pair, tuple) else (pair, None)
        out = []
        request = req_text(entry) if entry else ""
        rid = (entry or {}).get("id", "?")
        asked = _HEADER_SET_RE.search(request) if entry else None
        out.append(_check(
            "the request asked for a header", asked is not None,
            f"{asked.group(1)}: {asked.group(2).strip()[:40]} in {rid}"
            if asked else
            "no cited request carries a CRLF sequence followed by "
            "`name: value` - a bare %0d%0a with nothing after it splits "
            "nothing"))
        name = (asked.group(1) if asked else "").strip()
        want = (asked.group(2) if asked else "").strip()
        got = header_of(entry, name) if (entry and name) else ""
        # the value may be normalised (whitespace, case in a token), so
        # containment is the honest test, not equality
        landed = bool(got) and bool(want) and (
            want.lower() in got.lower() or got.lower() in want.lower())
        out.append(_check(
            "the response carries it as a header", landed,
            f"{name}: {got[:60]} in {rid}" if landed else
            (f"the response has no {name!r} header - the payload was "
             "reflected into the body at most" if name and not got else
             f"{name}: {got[:40]} does not carry the injected value"
             if name else "no header name to look for")))
        # The control has to be the SAME endpoint. Without that check, any
        # exchange that happens not to carry the header counts as the
        # control - including one to a different host entirely, which says
        # nothing about whether THIS endpoint always sends it.
        same_endpoint = control is not None and entry is not None and \
            _endpoint_shape(control) == _endpoint_shape(entry)
        control_clean = None
        if same_endpoint and name:
            control_clean = not header_of(control, name)
        out.append(_check(
            "a control response does not carry it", bool(control_clean),
            f"absent from {control.get('id')}" if control_clean else
            ("no control exchange cited; a header that is always present is "
             "not one the request created" if control is None else
             f"{control.get('id')} is a different endpoint - a control has "
             "to be the same one, or it says nothing about what this "
             "endpoint always sends" if not same_endpoint else
             f"{control.get('id')} carries {name!r} too - the server sends "
             "that header regardless")))
        return out

    return _witness(_pairs(claim.exchanges) or [(None, None)], build,
                    ("the request asked for a header",
                     "the response carries it as a header",
                     "a control response does not carry it"))


# Content types a browser acts on. `text/plain` is not here on purpose: a
# `.svg` or `.html` served as text/plain is inert, and treating a stored file
# as dangerous because of its NAME rather than how it is served is the
# mistake this class kept making.
ACTIVE_CTYPE_RE = re.compile(
    r"(?i)^\s*(?:text/html|application/xhtml\+xml|image/svg\+xml"
    r"|application/javascript|text/javascript|application/ecmascript"
    r"|text/xsl|application/xml\+xhtml)\b")
MULTIPART_RE = re.compile(r'(?i)filename\s*=\s*"?([^"\r\n;]{1,200})')


_PART_RE = re.compile(
    r"(?is)filename\s*=[^\r\n]*\r?\n(?:[^\r\n]+\r?\n)*\r?\n(.*?)\r?\n--")


def _uploaded_part(entry: dict) -> str:
    """The file content inside a multipart upload request, if there is one.

    Needed because "the nonce came back" does not distinguish the stored file
    from a page that names it - only comparing against what was actually sent
    does.
    """
    body = str(_req(entry).get("body") or "")
    match = _PART_RE.search(body)
    return match.group(1).strip() if match else ""


def verify_served_upload(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """An uploaded file served back as something a browser will act on.

    The note said "serving is not executing", which is true and was being
    used to cap a class whose own requirement sentence already handles the
    execution case: code execution IS an rce finding and is graded as one.
    What is left is the thing this evidence can settle - a file the tester
    uploaded, served back with its bytes intact and a content-type that makes
    those bytes script.

    The content-type is the whole discriminator, and it is the part nothing
    was checking. A `.svg` served as `text/plain` is inert; the same bytes as
    `image/svg+xml` run in the uploader's origin. A `Content-Disposition:
    attachment` neutralises it again, so a response carrying one does not
    pass.
    """
    def build(pair) -> list[dict]:
        up, fetch = pair if isinstance(pair, tuple) else (pair, None)
        out: list[dict] = []
        request = req_text(up) if up else ""
        named = MULTIPART_RE.search(request) if up else None
        nonces = {m.group(0) for m in NONCE_RE.finditer(request)}
        uploaded = bool(named and nonces)
        out.append(_check(
            "a file was uploaded with a probe nonce in it", uploaded,
            f"{named.group(1)[:60]} in {(up or {}).get('id', '?')}"
            if uploaded else
            ("the cited request carries a filename but no probe nonce - "
             "without one the served bytes cannot be tied to this upload"
             if named else
             "no cited request is a multipart upload naming a file")))

        body = resp_body(fetch) if fetch else ""
        back = sorted(n for n in nonces if n in body)
        # The response has to BE the file, not a page that mentions it. An
        # "Upload complete - saved <your svg>" confirmation page carries the
        # nonce too, and served as text/html it satisfied every other check
        # here: this graded `proven` against an app that stored nothing.
        content = _uploaded_part(up) if up else ""
        stripped = body.strip()
        dominant = bool(content) and content in stripped and \
            len(content) >= 0.5 * max(len(stripped), 1)
        # Three things this was not checking, each of which let a benign
        # pair through: the upload has to have been ACCEPTED (a refused
        # upload plus any page serving the same bytes graded proven), the
        # fetch has to be on the SAME HOST (a foreign host serving a copy
        # says nothing about this target), and it has to come AFTER the
        # upload (a page recorded earlier cannot be the stored file). Found
        # by an adversarial audit of this session's own code.
        up_ok = bool(up) and 200 <= status_of(up) < 400
        same_host = (fetch is not None and up is not None
                     and _endpoint_shape(fetch).split("/")[0]
                     == _endpoint_shape(up).split("/")[0])
        after = (fetch is not None and up is not None
                 and claim.exchanges.index(fetch)
                 > claim.exchanges.index(up))
        served = bool(uploaded and up_ok and fetch is not None and back
                      and dominant and same_host and after
                      and 200 <= status_of(fetch) < 300)
        out.append(_check(
            "it is served back with the bytes intact", served,
            f"{back[0]} returned by {fetch.get('id')}, {len(content)} of "
            f"{len(stripped)} bytes" if served else
            ("no second exchange cited; the proof is the fetch, not the "
             "upload response" if fetch is None else
             f"{(up or {}).get('id', '?')} answered {status_of(up)} - the "
             "upload was refused, so nothing of ours was stored"
             if not up_ok else
             f"{fetch.get('id')} is on a different host than the upload - a "
             "copy served elsewhere says nothing about this target"
             if not same_host else
             f"{fetch.get('id')} was recorded before the upload, so it "
             "cannot be the stored file" if not after else
             f"{fetch.get('id')} answered {status_of(fetch)}"
             if not 200 <= status_of(fetch) < 300 else
             f"nothing this upload carried appears in {fetch.get('id')} - "
             "the file was not stored, or is served from elsewhere"
             if not back else
             "the upload request carries no readable file part to compare "
             "against" if not content else
             f"the uploaded bytes are {len(content)} of {len(stripped)} in "
             f"{fetch.get('id')} - a page that mentions the upload is not "
             "the stored file")))

        ctype = header_of(fetch, "content-type") if fetch else ""
        disposition = header_of(fetch, "content-disposition") if fetch else ""
        attached = "attachment" in disposition.lower()
        active = bool(served and ACTIVE_CTYPE_RE.match(ctype) and not attached)
        # The detail has to say what is actually wrong. It read "served as
        # text/html - inert" whenever an EARLIER check failed, which is a
        # false statement about an active type and sends a reader to fix the
        # wrong thing.
        type_is_active = bool(ACTIVE_CTYPE_RE.match(ctype)) and not attached
        out.append(_check(
            "served with a content-type a browser acts on", active,
            f"{ctype.strip()[:60]}" if active else
            (f"served as attachment ({disposition.strip()[:40]}) - the "
             "browser downloads it rather than running it" if attached else
             f"{ctype.strip()[:40]} would be acted on, but the check above "
             "did not find the stored file in that response"
             if type_is_active else
             f"served as {ctype.strip()[:40] or '(no content-type)'} - inert, "
             "whatever the file is called")))
        return out

    return _witness(_pairs(claim.exchanges) or [(None, None)], build,
                    ("a file was uploaded with a probe nonce in it",
                     "it is served back with the bytes intact",
                     "served with a content-type a browser acts on"))


def _window(entry: dict) -> tuple[float, float]:
    """When this request was on the wire, as [start, end].

    `ts` is stamped when the exchange is RECORDED, which is after the
    response arrived, so it is the end of the window and `elapsed_ms` gives
    the start. An entry missing either is a zero-width window: it overlaps
    nothing, which is the fail-closed answer.
    """
    try:
        end = float(entry.get("ts") or 0.0)
    except (TypeError, ValueError):
        return (0.0, 0.0)
    resp = entry.get("response") if isinstance(entry, dict) else None
    try:
        elapsed = float((resp or {}).get("elapsed_ms") or 0.0) / 1000.0
    except (TypeError, ValueError):
        elapsed = 0.0
    if not end or elapsed <= 0:
        return (0.0, 0.0)
    return (end - elapsed, end)


def _overlaps(a: dict, b: dict) -> bool:
    (s1, e1), (s2, e2) = _window(a), _window(b)
    if not e1 or not e2:
        return False
    return s1 < e2 and s2 < e1


# Statuses that say "this action cannot be done again", as distinct from
# missing (404), moved (3xx), broken (5xx) or throttled (429).
_SPENT_STATUS = (400, 403, 409, 410, 423)
_THROTTLE_RE = re.compile(r"(?i)too many requests|rate.?limit|slow down")


def _spent_refusal(entry: dict, won: list[dict]) -> bool:
    """Does this exchange say the action was already spent?

    Any non-2xx used to count, which made a 404 after three cacheable GETs
    into a race. The refusal is the ONLY thing in this class's evidence that
    establishes there was a limit, so it has to actually say so - and it has
    to be a different answer than the one the burst got, or it is not a
    refusal of anything.
    """
    status = status_of(entry)
    if status not in _SPENT_STATUS:
        return False
    text = resp_text(entry)
    if header_of(entry, "retry-after") or _THROTTLE_RE.search(text):
        return False                      # throttling is not a limit crossed
    body = resp_body(entry).strip()
    return all(body != resp_body(w).strip() for w in won)


def verify_concurrent_crossing(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A limited action crossed under concurrency, with the limit shown.

    The note said "no serial control is measured", which was true of the
    verifier and false of the probe: `probe_race` sends the serial baseline
    and the transcript stamps every exchange with `ts` and `elapsed_ms`, so
    the overlap is reconstructable from the record rather than taken on the
    probe's word.

    Three things, and the third is the one that makes it a race rather than a
    repeatable action:

    1. two attempts at the same action were **on the wire at the same time**
       - windows that intersect, not merely adjacent request ids;
    2. more than one of them succeeded;
    3. a **serial** attempt, after the burst, did not. Without that, "two
       requests succeeded" says the action is repeatable, which is not a bug.
    """
    checks: list[dict] = []
    groups: dict[str, list[dict]] = {}
    for entry in claim.exchanges:
        key = f"{_method_of(entry)} {_endpoint_shape(entry)}"
        groups.setdefault(key, []).append(entry)

    best: tuple[int, list[dict], list[dict], str] = (0, [], [], "")
    for key, entries in groups.items():
        ordered = sorted(entries, key=lambda e: _window(e)[0])
        for i, first in enumerate(ordered):
            burst = [first] + [o for o in ordered[i + 1:]
                               if _overlaps(first, o)]
            if len(burst) < 2:
                continue
            won = [e for e in burst if 200 <= status_of(e) < 300]
            burst_end = max(_window(e)[1] for e in burst)
            after = [e for e in ordered
                     if _window(e)[0] >= burst_end
                     and not any(_overlaps(e, o) for o in ordered
                                 if o is not e)]
            refused = [e for e in after if _spent_refusal(e, won)]
            score = (len(burst) >= 2) + (len(won) >= 2) + bool(refused)
            if score > best[0]:
                best = (score, burst, refused, key)
    _, burst, refused, key = best
    won = [e for e in burst if 200 <= status_of(e) < 300]

    checks.append(_check(
        "two attempts were on the wire at once", len(burst) >= 2,
        f"{len(burst)} overlapping requests to {key}" if len(burst) >= 2 else
        "no two cited exchanges to one endpoint have intersecting "
        "[start, end] windows - adjacent request ids are not concurrency, "
        "and a burst the server serialized cannot evidence a race"))
    checks.append(_check(
        "more than one of them succeeded", len(won) >= 2,
        f"{len(won)} of {len(burst)} answered 2xx" if len(won) >= 2 else
        f"{len(won)} of {len(burst) or 0} succeeded - one success in a burst "
        "is the action working once, as designed"))
    checks.append(_check(
        "a serial attempt afterwards was refused", bool(refused),
        f"{refused[0].get('id')} answered {status_of(refused[0])} after the "
        f"burst" if refused else
        "no non-overlapping attempt after the burst was refused AS SPENT - "
        "any non-2xx used to count here, so three read-only GETs and a later "
        "404 graded proven. A 404 says the thing is missing, a 3xx says it "
        "moved, a 5xx says the server broke and a 429 says you were too "
        "fast; none of them says the action had a limit that was crossed"))
    return checks


# A method name no client sends: the stray byte left in the stream prefixes
# the next request line, so a desynced back end answers about `GPOST`, `GGET`
# and friends. A generic "400 Bad Request" names nothing and proves nothing.
# `G` PREFIXED to a real verb, which is what the stray byte produces. The
# second and third alternatives used to be `G[A-Z]{2,}`, which matches `GET`
# itself - so any response body containing `"method": "GET"`, `(GET)` or
# `method GET not allowed` satisfied the desync check. Found by an
# adversarial audit of this session's own code.
_VERBS = "GET|POST|PUT|HEAD|DELETE|OPTIONS|PATCH|TRACE|CONNECT"
BOGUS_METHOD_RE = re.compile(
    r"(?:\bG(?:" + _VERBS + r")\b"
    r"|['\"(\s]G(?:" + _VERBS + r")['\")\s]"
    r"|method\s+'?G(?:" + _VERBS + r")\b)")
# Both framings declared on one request is the ambiguity itself.
_CL_RE = re.compile(r"(?im)^\s*content-length\s*:", re.M)
_TE_RE = re.compile(r"(?im)^\s*transfer-encoding\s*:", re.M)


def _wire_text(entry: dict) -> str:
    """The request as it went on the wire, if the recorder kept it.

    `send_raw` keeps `request_text` precisely because a headers dict
    collapses duplicates - and a duplicated or conflicting framing header
    pair IS the evidence for this class.
    """
    req = _req(entry)
    text = str(req.get("request_text") or "")
    if text:
        return text
    headers = req.get("headers") if isinstance(req.get("headers"), dict) else {}
    return "\n".join(f"{k}: {v}" for k, v in headers.items())


def verify_desync(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Request smuggling: two framings declared, and the connection confused.

    The note said this system "sends the desync pair and reads the
    difference, which is a candidate". The difference was never the
    evidence; the recorded artefact is, and `probe_smuggle` has been
    recording it all along - `send_raw` keeps the wire text, so a request
    carrying both `Content-Length` and `Transfer-Encoding` is visible, and
    it keeps unsolicited responses from an extra read, so a response that
    arrived with no request of its own is visible too.

    Two shapes count, and they are the two the probe sends:

    * **TE.CL** - the smuggled request line is complete, so the poisoned
      response arrives on its own. In the transcript that is an entry whose
      request method is `-`: a response nothing asked for, which is the
      requirement sentence almost word for word.
    * **CL.TE** - the stray byte prefixes OUR next request line, so the
      answer comes back naming a method no client sends. The response was
      solicited, but the method it complains about was not sent by anyone.

    Either way the second check is the one that matters: a bogus method
    named back. A 4xx with no method in it is a server disliking the request,
    which is what an ambiguous request deserves and not a desync.
    """
    exchanges = claim.exchanges
    checks: list[dict] = []

    ambiguous = [e for e in exchanges
                 if _CL_RE.search(_wire_text(e)) and _TE_RE.search(_wire_text(e))]
    checks.append(_check(
        "the request declared two conflicting framings", bool(ambiguous),
        f"Content-Length and Transfer-Encoding both on "
        f"{ambiguous[0].get('id')}" if ambiguous else
        "no cited request carries both Content-Length and Transfer-Encoding "
        "- without the ambiguity there is nothing for a front end and a back "
        "end to disagree about"))

    desync, detail = None, "no response names a method the probe never sent"
    if ambiguous:
        # Order by position in the cited list, not by parsing `r<n>` out of
        # the id. The ids are the recorder's business, and an id this
        # verifier cannot parse made it raise rather than refuse - which
        # `grade()` reports as "evidence is readable", hiding the real answer.
        first = min(exchanges.index(e) for e in ambiguous)
        shapes = {_endpoint_shape(e) for e in ambiguous}
        for position, entry in enumerate(exchanges):
            if position <= first:
                continue              # before the ambiguity: not its effect
            if _endpoint_shape(entry) not in shapes:
                continue
            hit = BOGUS_METHOD_RE.search(resp_body(entry))
            if not hit:
                continue
            # the effect exchange must not have asked about that method
            # itself: a server naming back a verb the request carried is an
            # echo, and in a real desync the poisoned name arrives from the
            # OTHER request's leftover bytes
            if BOGUS_METHOD_RE.search(req_text(entry)):
                detail = (f"{entry.get('id')} names "
                          f"{hit.group(0).strip()!r} back, but its own "
                          "request carries it - that is an echo, not a "
                          "desync")
                continue
            unsolicited = _method_of(entry) == "-"
            desync = (entry, hit.group(0).strip(), unsolicited)
            break
    if desync is not None:
        entry, named, unsolicited = desync
        detail = (f"{entry.get('id')} answered about {named!r} "
                  + ("with no request of its own - the back end was "
                     "answering a request the front end never sent"
                     if unsolicited else
                     "- the stray bytes prefixed the next request line"))
    checks.append(_check("the connection's framing was desynchronised",
                         desync is not None, detail))
    return checks


_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def verify_websocket_channel(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A cross-origin handshake accepted, and a message the channel answered.

    The note said "needs a real WebSocket client. This system compares the
    handshake only" - which was true, and was a missing client rather than a
    missing proof. `GuardedClient.send_ws` is that client now, so both halves
    are on record and both are checkable here.

    Three checks, and each rules out a different wrong conclusion:

    1. **the handshake was accepted** - a 101 whose `Sec-WebSocket-Accept` is
       the SHA-1 of the key this request sent plus the RFC 6455 GUID. A
       middleware or mock that answers 101 without completing the challenge
       is not a WebSocket endpoint, and recomputing the token is the only way
       to tell from the record;
    2. **from an origin the target does not own** - the whole class is that a
       foreign page can open this channel. A same-origin handshake succeeding
       is a WebSocket endpoint working as designed;
    3. **and the channel answered a message** - a frame carrying a nonce this
       claim's own frame sent. A 101 followed by silence is not a hijackable
       channel; it is a handshake.

    What it does not show, and the requirement does not claim: that the
    answer contained anything the caller should not reach. This grades the
    channel being open cross-origin, which is the finding. Data taken over
    it is a different class and is graded as one.
    """
    import base64 as _b64
    import hashlib as _hashlib

    exchanges = claim.exchanges
    checks: list[dict] = []

    def _accept_ok(entry: dict) -> bool:
        headers = _req_headers(entry)
        key = next((v for k, v in headers.items()
                    if k.lower() == "sec-websocket-key"), "")
        got = header_of(entry, "sec-websocket-accept")
        if not key or not got:
            return False
        want = _b64.b64encode(_hashlib.sha1(
            (str(key).strip() + _WS_GUID).encode()).digest()).decode()
        return got.strip() == want

    handshakes = [e for e in exchanges
                  if status_of(e) == 101 and _accept_ok(e)]
    checks.append(_check(
        "the handshake completed the RFC 6455 challenge",
        bool(handshakes),
        f"101 with a valid accept token in {handshakes[0].get('id')}"
        if handshakes else
        ("no cited exchange is a 101 whose Sec-WebSocket-Accept is the SHA-1 "
         "of the key it sent - a 101 without the challenge is middleware or "
         "a mock, not a WebSocket endpoint")))

    foreign, why = None, ""
    for entry in handshakes:
        origin = next((v for k, v in _req_headers(entry).items()
                       if k.lower() == "origin"), "")
        if not origin:
            why = (f"{entry.get('id')} sent no Origin - a handshake with no "
                   "Origin says nothing about whether a foreign page could "
                   "make it")
            continue
        o_host = (urllib.parse.urlparse(str(origin)).hostname or "").lower()
        t_host = (urllib.parse.urlparse(
            str(_req(entry).get("url") or "")).hostname
            or "").lower()
        if o_host and t_host and o_host != t_host:
            foreign = (entry, origin)
            break
        why = (f"{entry.get('id')} sent Origin {origin} on a channel at "
               f"{t_host} - a same-origin handshake is the endpoint working")
    checks.append(_check(
        "accepted from an origin the target does not own",
        foreign is not None,
        f"Origin {foreign[1]} accepted on {foreign[0].get('id')}"
        if foreign else (why or "no handshake to check an Origin on")))

    answered, detail = None, "no frame on record"
    if foreign is not None:
        shape = _endpoint_shape(foreign[0])
        for entry in exchanges:
            if _method_of(entry) != "WSFRAME":
                continue
            if _endpoint_shape(entry) != shape:
                detail = (f"{entry.get('id')} is a frame on a different "
                          "endpoint than the handshake")
                continue
            sent = str((_req(entry).get("body") or ""))
            got = resp_body(entry)
            back = [m.group(0) for m in NONCE_RE.finditer(sent)
                    if m.group(0) in got]
            if back:
                answered = (entry, back[0])
                break
            detail = (f"{entry.get('id')} carries no probe nonce that its own "
                      "frame sent - without one the answer cannot be tied to "
                      "this channel")
    checks.append(_check(
        "the channel answered a message", answered is not None,
        f"{answered[1]} sent and returned on {answered[0].get('id')}"
        if answered else detail))
    return checks


_WRITE_METHODS = ("PUT", "DELETE", "PATCH")


def _method_of(entry: dict) -> str:
    return str(_req(entry).get("method") or "").upper()


def verify_method_effect(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """A method that should be refused, honoured, with the effect observed.

    The note said "a status difference is not an effect", which was right
    about `verify_generic` and wrong about the evidence: `probe_method`
    already records both shapes of effect this class can have, and both are
    pairs.

    **A write that landed.** `PUT /x` answered 2xx, and a later `GET /x`
    returned the bytes the PUT carried. The status alone proves nothing - an
    endpoint can answer 201 and discard the body - so the read-back is the
    check that matters.

    **TRACE enabled.** `TRACE` answered, and the response body contains a
    value that was only ever in the request's HEADERS. That is cross-site
    tracing: it hands HttpOnly cookies and auth headers to a reading XSS. The
    echo IS the finding here, as with xss and crlf, which is why the class
    sets `reflection_is_the_finding`.

    Both paths emit the same two check names, so the floor means the same
    thing either way: an effect was observed, not merely a status.
    """
    def build(pair) -> list[dict]:
        a, b = pair if isinstance(pair, tuple) else (pair, None)
        out: list[dict] = []
        method = _method_of(a) if a else ""
        status = status_of(a) if a else 0
        answered = bool(a) and 200 <= status < 300
        # "the endpoint SHOULD refuse it" is the half this check was missing:
        # a REST API that honours PUT on its own resource is doing its job,
        # and grading that as verb tampering called every correct API a
        # finding. Evidence that the method is not meant to be available:
        #   * TRACE - no application needs it reachable, and an echo of a
        #     request header is cross-site tracing on its own;
        #   * an OPTIONS/Allow list that does NOT advertise the method;
        #   * the same method refused somewhere else on the same host, so the
        #     one that was honoured is the exception.
        # Found by an adversarial audit of this session's own code.
        advertised, refused_elsewhere = None, None
        if a is not None and method in _WRITE_METHODS:
            # _endpoint_shape is "host/path-shape", so the host is the first
            # segment - slicing [0:3] took two path segments with it and made
            # "the same host" mean "the same first two path segments"
            host = _endpoint_shape(a).split("/")[0]
            for other in (claim.exchanges or []):
                if other is a:
                    continue
                allow = header_of(other, "allow") or header_of(
                    other, "access-control-allow-methods")
                if allow and _endpoint_shape(other) == _endpoint_shape(a):
                    advertised = allow
                if (_method_of(other) == method
                        and status_of(other) in (403, 405, 501)
                        and _endpoint_shape(other).split("/")[0] == host):
                    refused_elsewhere = other
        unadvertised = advertised is not None and \
            method not in str(advertised).upper()
        should_refuse = (method == "TRACE" or unadvertised
                         or refused_elsewhere is not None)
        honoured = answered and bool(method) and should_refuse
        if honoured:
            why = (f"{method} answered {status} on {(a or {}).get('id', '?')}"
                   + (" and no application needs TRACE reachable"
                      if method == "TRACE" else
                      f", and Allow says {advertised!r}" if unadvertised else
                      f", and {refused_elsewhere.get('id')} was refused "
                      f"{status_of(refused_elsewhere)} for the same method"))
        elif not answered:
            why = (f"{method or 'no'} {status or ''} - the cited request is "
                   "not a write or a TRACE that was answered".strip())
        elif method not in _WRITE_METHODS and method != "TRACE":
            why = (f"{method} is not a method this class is about; "
                   f"{', '.join(_WRITE_METHODS)} or TRACE")
        else:
            why = (f"{method} answered {status}, but nothing on record says "
                   "this endpoint should have refused it - a REST API that "
                   "honours PUT on its own resource is doing its job. Cite "
                   "an OPTIONS whose Allow omits it, or the same method "
                   "refused elsewhere on the host")
        out.append(_check(
            "a method the endpoint should refuse was honoured", honoured,
            why))

        effect, detail = False, "no effect observed"
        if honoured and method == "TRACE":
            # a value that was in the REQUEST HEADERS and came back in the body
            headers = " ".join(f"{k}: {v}" for k, v in
                               _req_headers(a).items())
            echoed = [m.group(0) for m in NONCE_RE.finditer(resp_body(a))
                      if m.group(0) in headers]
            effect = bool(echoed)
            detail = (f"{echoed[0]} was sent as a request header and came "
                      f"back in the body of {a.get('id')}" if effect else
                      "the TRACE response echoes no probe nonce that was "
                      "sent as a request header - without one, the echo "
                      "cannot be tied to this probe")
        elif honoured and b is not None:
            # the read-back: a GET to the same path returning written bytes
            same = _path_of(a) == _path_of(b) and _endpoint_shape(a) == \
                _endpoint_shape(b)
            # The nonce has to come from the request BODY, not from
            # `req_text`, which includes the URL. With the URL in scope, a
            # PUT of inert bytes to /up/<nonce>.txt plus a directory listing
            # that echoes the filename graded `proven` - the effect proven
            # was the server printing a name back, not storing anything.
            wrote = str(_req(a).get("body") or "")
            read = resp_body(b)
            carried = [m.group(0) for m in NONCE_RE.finditer(wrote)
                       if m.group(0) in read]
            effect = bool(same and _method_of(b) == "GET"
                          and 200 <= status_of(b) < 300 and carried)
            if effect:
                detail = (f"{carried[0]} was written by {a.get('id')} and "
                          f"read back by {b.get('id')}")
            elif not same:
                detail = (f"{b.get('id')} is a different path - the read-back "
                          "has to be of what was written")
            elif _method_of(b) != "GET":
                detail = f"{b.get('id')} is {_method_of(b)}, not a GET read"
            elif not 200 <= status_of(b) < 300:
                detail = (f"{b.get('id')} answered {status_of(b)} - the "
                          "written object is not readable")
            elif not wrote:
                detail = (f"{a.get('id')} carries no request body - a write "
                          "with nothing in it has no bytes to read back, and "
                          "a nonce in the URL only proves the server can "
                          "print a path")
            else:
                detail = (f"nothing the write BODY carried appears in "
                          f"{b.get('id')} - a 2xx on a write that discarded "
                          "the body is not an effect")
        elif honoured:
            detail = ("no second exchange cited; a write needs the read that "
                      "shows it landed")
        out.append(_check("the method had an observable effect", effect,
                          detail))
        return out

    return _witness(_pairs(claim.exchanges) or [(None, None)], build,
                    ("a method the endpoint should refuse was honoured",
                     "the method had an observable effect"))


def verify_generic(claim: Claim, spec: "ProofSpec") -> list[dict]:
    """Classes whose artifact this system measures as a difference and nothing
    more.

    These are capped at `candidate` by their spec's ceiling, because
    "these two responses differ" is true of any two pages on any site and used
    to grade seven classes `proven`. The requirement sentence says what would
    settle each one; this check says only that a difference is on record.
    """
    return [_discriminates(claim)]


def verify_refused(claim: Claim, spec: "ProofSpec") -> list[dict]:
    return [_check("class is provable by this system", False, spec.refusal)]


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
    ceiling: str = ""
    # WHY the ceiling is there. "unimplemented" means a verifier nobody has
    # written yet and the transcript already holds what it would need; any
    # other value is a reason labour will not fix. This was prose in two
    # documents and drifted from the matrix twice while classes came off the
    # list, so it is a field now and the doc gate counts it.
    cap_reason: str = ""
    declares: str = "command"
    advisories: tuple[str, ...] = ()
    # xss, prototype pollution and crlf are proven BY the reflection, so the
    # universal "the target produced these bytes" veto does not apply to them
    reflection_is_the_finding: bool = False

    def verify(self, claim: Claim) -> "Verdict":
        wire = _wire_check(claim)
        if self.verifier is verify_refused:
            checks = self.verifier(claim, self)
            return Verdict(self.vuln_class, "refused", checks,
                           [c["check"] for c in checks], self.requirement, self.notes)
        if not wire["ok"]:
            return Verdict(self.vuln_class, "unproven", [wire], [wire["check"]],
                           self.requirement, self.notes)
        echo = _echo_check(claim, self)
        checks = [wire, echo, *self.verifier(claim, self)]
        raw = _grade(checks, self.required,
                     (*self.veto, "the target produced the quoted bytes"),
                     self.floor)
        grade = _clamp(raw, self.ceiling)
        named = (*self.required, *self.veto, *self.floor,
                 "the target produced the quoted bytes")
        missing = [c["check"] for c in checks if not c["ok"] and c["check"] in named]
        warnings = [c["check"] for c in checks
                    if not c["ok"] and c["check"] in self.advisories]
        capped = ""
        if len(claim.exchanges) > _MAX_PAIRED:
            checks = [*checks, _check(
                "the citation is small enough to grade whole", False,
                f"{len(claim.exchanges)} exchanges cited; the first "
                f"{_MAX_PAIRED} were paired. A contrast needs two exchanges - "
                "cite the pair that proves it")]
        if grade != raw:
            # Otherwise the artifact says every check passed and `missing: []`
            # while the grade says candidate - a reader cannot tell whether the
            # evidence fell short or the class is capped, and the two mean
            # entirely different things.
            capped = _ceiling_reason(self)
            checks = [*checks, _check(
                f"settled by this system (held at {self.ceiling})", False,
                capped)]
            missing = [*missing,
                       f"settled by this system (held at {self.ceiling})"]
        return Verdict(self.vuln_class, grade, checks, missing,
                       self.requirement, self.notes, warnings, capped)


@dataclass
class Verdict:
    vuln_class: str
    grade: str
    checks: list[dict] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    requirement: str = ""
    notes: str = ""
    # failed checks that do not change the grade but must still be read: the
    # bug is proven AND the tester took more than the proof
    warnings: list[str] = field(default_factory=list)
    # set when the class's ceiling held the grade down rather than the evidence
    # falling short - the two are different facts and a reader needs both
    capped: str = ""

    @property
    def proven(self) -> bool:
        return self.grade == "proven"

    def to_dict(self) -> dict:
        out = {"vuln_class": self.vuln_class, "grade": self.grade,
               "requirement": self.requirement, "checks": self.checks}
        if self.missing:
            out["missing"] = self.missing
        if self.warnings:
            out["warnings"] = self.warnings
        if self.capped:
            out["capped_by_this_system"] = self.capped
        return out

    def explain(self) -> str:
        lines = [f"{self.vuln_class}: {self.grade}", f"  requires: {self.requirement}"]
        for check in self.checks:
            lines.append(f"  [{'x' if check['ok'] else ' '}] {check['check']}"
                         + (f" - {check['detail']}" if check.get("detail") else ""))
        return "\n".join(lines)


RCE_REQUIRED = ("a benign command was sent", "identity output returned by the target",
                "the probe nonce came back in the output")
RCE_VETO = ("proof command stayed benign",)
SQLI_REQUIRED = ("data store fingerprinted", "the query named its target",
                 "rows returned, not an error message")
# Not a veto and not a requirement. The bug is real either way; taking more
# than the proof is a conduct problem, so it is reported rather than graded -
# it used to be in no set at all, which meant it was never even printed.
EXTRACTION_ADVISORY = ("extraction stayed minimal",)
DESERIALIZE_REQUIRED = ("a serialized payload was sent",
                        "identity output returned by the target",
                        "the probe nonce came back in the output")
EXTRACTION_REQUIRED = ("the query named its target",
                       "rows returned, not an error message")
# A document store has no FROM clause, so there is no request-side evidence of
# a READ - only of an attempt. nosqli therefore carries one more required
# check than sqli: the response has to show a document shape. Without it, a
# search box reflecting `{"$ne": null}` into its "no results" line satisfied
# every check and graded `proven` on a page with no database behind it.
DOCUMENT_REQUIRED = ("the query named its target",
                     "documents came back, not the payload",
                     "rows returned, not an error message")
# nosqli had no floor at all, so one exchange that merely carried an operator
# query graded `proven` - including one whose response refused it.
EXTRACTION_FLOOR = ("rows returned, not an error message",)
DOCUMENT_FLOOR = ("documents came back, not the payload",
                  "rows returned, not an error message")

#: Classes whose cap is a verifier nobody has written. The transcript already
#: records what each would need, so these are labour.
CAP_UNIMPLEMENTED = "unimplemented"

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
              "serialized payload: the gadget sent, the identity line and the "
              "nonce returned",
              DESERIALIZE_REQUIRED, verify_command_output, veto=RCE_VETO,
              # the GADGET is what makes this class rather than rce, so it is
              # the floor: with the floor on the identity line, a page that
              # happened to print `uid=0(root)` graded deserialize a candidate
              floor=("a serialized payload was sent",),
              declares="serialized",
              aliases=("deserialization", "insecure-deserialization", "pickle",
                       "java-deserialization")),
    ProofSpec("sqli", "the DBMS fingerprint plus at least one row from a named "
              "table, bounded to what proves the read",
              SQLI_REQUIRED, verify_data_extraction,
              advisories=EXTRACTION_ADVISORY,
              aliases=("sql-injection", "sqlinjection", "blind-sqli",
                       "second-order-sqli"),
              notes="Five rows is a proof. A full dump is an incident."),
    ProofSpec("nosqli", "an operator query that CHANGED what the store "
              "answered, against a control to the same endpoint without it - "
              "either a refusal turned into access, or documents a control "
              "does not return",
              ("the request carried an operator query",
               "the operator changed what the store answered",
               "the quoted bytes are the access, not an error"),
              verify_operator_injection, fingerprint=False,
              advisories=EXTRACTION_ADVISORY,
              floor=("the operator changed what the store answered",
                     "the quoted bytes are the access, not an error"),
              aliases=("nosql-injection", "mongo-injection")),
    ProofSpec("graphql", "a GraphQL query the endpoint answered with its "
              "schema or with records the caller should not reach",
              ("a GraphQL query was sent",
               "the endpoint answered with schema or records"),
              verify_graphql,
              floor=("the endpoint answered with schema or records",),
              aliases=("graphql-exposure", "graphql-introspection")),
    ProofSpec("lfi", "a request that asked for a file, a sentinel from a file "
              "whose contents are known, and a control path that does not exist",
              ("the request asked for a file", "known-file sentinel observed",
               "negative control recorded"),
              verify_file_read, floor=("the request asked for a file",),
              aliases=("file-read", "fileread", "path-traversal", "pathtraversal",
                       "arbitrary-file-read", "directory-traversal", "rfi")),
    ProofSpec("xxe", "a local file read through the parser, from a request "
              "that declared the entity",
              ("the request asked for a file", "known-file sentinel observed"),
              verify_file_read, floor=("the request asked for a file",),
              aliases=("xml-external-entity",)),
    ProofSpec("ssti", "an arithmetic result rendered by the template engine, "
              "with the expression itself absent from the response",
              ("expression evaluated, not echoed",
               "a second operand pair confirms it"), verify_template_eval,
              floor=("expression evaluated, not echoed",),
              aliases=("template-injection", "el-injection", "expression-injection")),
    ProofSpec("idor", "one actor reaching another's subject on the same "
              "endpoint, with subject-identifying data and nothing entitling "
              "the caller to it",
              ("two distinct object references on one endpoint",
               "another subject's data returned", "the data identifies a subject",
               "the caller was not entitled to it"),
              verify_differential,
              # the check that makes the evidence ABOUT access control. With
              # the floor on "another subject's data returned" - which is any
              # excerpt present in one cited response and absent from another -
              # two pages of a paginated list graded as a candidate.
              floor=("the data identifies a subject",),
              aliases=("bola", "authorization-bypass", "broken-access-control",
                       "access-control")),
    ProofSpec("massassign", "a privileged field the caller sent, set on the "
              "server and shown set by a later read",
              ("a privileged field was sent and accepted",
               "a later read shows it set"),
              verify_mass_assignment,
              floor=("a privileged field was sent and accepted",),
              aliases=("mass-assignment", "massassignment",
                       "parameter-binding", "autobinding")),
    ProofSpec("jwt", "a credential this system minted, accepted on a "
              "privileged resource with its claims echoed back, and another "
              "credential refused on the same endpoint",
              ("this system minted the credential",
               "a forged credential was accepted",
               "the same endpoint refuses another credential"),
              verify_token_forgery,
              # the mint is what makes this class: a good credential accepted
              # and a bad one refused is an auth system working, and with the
              # floor elsewhere every authenticated endpoint became a candidate
              floor=("this system minted the credential",),
              aliases=("auth-bypass", "authbypass", "jwt-forgery",
                       "session-fixation", "mfa-bypass", "auth")),
    ProofSpec("redirect", "a 3xx Location pointing off origin, with the in-origin "
              "control showing the destination parameter is honoured",
              ("the Location points off origin, to a host we supplied",
               "control recorded for the expected outcome"),
              verify_off_origin_redirect,
              floor=("the Location points off origin, to a host we supplied",),
              aliases=("open-redirect", "openredirect")),
    ProofSpec("cache", "a value only the poisoning request sent, returned to a "
              "requester that did not send it",
              ("the value reached a requester that did not send it",
               "the injecting request is on record"),
              verify_unkeyed_input,
              floor=("the value reached a requester that did not send it",),
              aliases=("cache-poisoning", "cachepoisoning", "web-cache-deception",
                       "cache-deception")),
    ProofSpec("smuggle", "a request declaring two framings, and the back end "
              "answering about a method no client sends - either on a "
              "response nothing asked for (TE.CL) or on the probe's own next "
              "request line (CL.TE)",
              ("the request declared two conflicting framings",
               "the connection's framing was desynchronised"),
              verify_desync,
              floor=("the connection's framing was desynchronised",),
              aliases=("request-smuggling", "requestsmuggling", "desync",
                       "cl-te", "te-cl")),
    ProofSpec("xfh", "restricted content returned when an ACL-relevant header "
              "is added, with the control showing the same request refused "
              "without it",
              ("restricted content returned with the header",
               "the same request is refused without it"),
              verify_restricted_access,
              floor=("restricted content returned with the header",),
              aliases=("host-header", "hostheader", "x-original-url",
                       "acl-bypass", "header-acl-bypass"),
              notes="Quote the restricted content, not the header you sent."),
    ProofSpec("cors", "a FOREIGN origin reflected in Access-Control-Allow-Origin "
              "with credentials allowed - an allowlist echoing the site's own "
              "origin is the defence working",
              ("a foreign probe origin is reflected",
               "credentials are allowed with it"),
              verify_cors, floor=("a foreign probe origin is reflected",)),
    ProofSpec("xss", "a headless browser executing the payload and reporting the "
              "probe nonce",
              ("payload reflected unencoded into HTML",
               "a real browser executed it"),
              verify_browser_execution, ceiling="candidate",
              cap_reason="no browser ships with this package",
              aliases=("reflected-xss", "stored-xss", "dom-xss",
                       "reflection"),
              reflection_is_the_finding=True),
    ProofSpec("ppoll", "a property only the polluting request sent, observed "
              "in a later read that did not send it - which is what the "
              "server-side half of prototype pollution looks like. A browser "
              "is needed only for the client-side variant",
              ("the value reached a requester that did not send it",
               "the injecting request is on record"),
              verify_unkeyed_input,
              floor=("the value reached a requester that did not send it",),
              aliases=("prototype-pollution", "prototypepollution")),
    ProofSpec("csrf", "a state-changing request that carried no anti-CSRF "
              "token, sent cross-origin, with the change shown by a read "
              "before and a read after",
              ("the state-changing request succeeded",
               "the state-changing request carried no anti-CSRF token",
               "it was sent cross-origin", "the state changed between two reads"),
              verify_state_change,
              floor=("the state-changing request succeeded",),
              aliases=("logic-flaw", "logicflaw", "business-logic")),
    ProofSpec("race", "two attempts at one limited action overlapping on the "
              "wire, both succeeding, and a serial attempt afterwards "
              "refused - the refusal is what shows there was a limit",
              ("two attempts were on the wire at once",
               "more than one of them succeeded",
               "a serial attempt afterwards was refused"),
              verify_concurrent_crossing,
              floor=("more than one of them succeeded",
                     "a serial attempt afterwards was refused"),
              aliases=("race-condition", "racecondition",
                       "toctou", "limit-overrun")),
    ProofSpec("disclosure", "the credential or source observed in a response, "
              "quoted as the bytes that leaked",
              ("a credential-shaped secret was observed",
               "it came from a response, not from the request"),
              verify_secret_leak, floor=("a credential-shaped secret was observed",),
              # named explicitly so the rename cannot orphan it again
              aliases=("info-disclosure", "infodisclosure", "information-disclosure",
                       "secret-exposure", "source-leak", "credential-leak")),
    ProofSpec("ssrf", "a callback at a collector we control carrying the probe "
              "nonce, or a response only the internal network could give. This "
              "system has no collector, so it measures the difference and stops "
              "at a candidate",
              ("the excerpt discriminates against a control",), verify_generic,
              ceiling="candidate",
              cap_reason="no out-of-band collector the target can reach",
              aliases=("server-side-request-forgery", "blind-ssrf")),
    ProofSpec("enum", "the same request giving two different answers for a "
              "known and an unknown account, each observed more than once",
              ("the same request gave two different answers",
               "each answer was observed more than once"),
              verify_oracle,
              floor=("the same request gave two different answers",),
              aliases=("user-enumeration", "enumeration", "username-enum",
                       "account-oracle")),
    ProofSpec("crlf", "a header the request asked for, present as a HEADER in "
              "the response and absent from a control to the same endpoint - "
              "not the payload reflected into the body",
              ("the request asked for a header",
               "the response carries it as a header",
               "a control response does not carry it"),
              verify_header_injection,
              floor=("the response carries it as a header",
                     "a control response does not carry it"),
              aliases=("header-injection", "response-splitting"),
              reflection_is_the_finding=True),
    ProofSpec("upload", "the uploaded file served back with its bytes intact "
              "AND a content-type a browser acts on - or executed, which is "
              "then an rce finding and graded as one",
              ("a file was uploaded with a probe nonce in it",
               "it is served back with the bytes intact",
               "served with a content-type a browser acts on"),
              verify_served_upload,
              floor=("it is served back with the bytes intact",
                     "served with a content-type a browser acts on"),
              aliases=("file-upload", "unrestricted-file-upload"),
              reflection_is_the_finding=True),
    ProofSpec("method", "a method the endpoint should refuse being honoured "
              "AND having an effect: a PUT whose bytes a later GET returns, "
              "or a TRACE that echoes a header the probe sent. A status "
              "difference alone is not an effect",
              ("a method the endpoint should refuse was honoured",
               "the method had an observable effect"),
              verify_method_effect,
              floor=("the method had an observable effect",),
              aliases=("http-method", "verb-tampering", "trace"),
              reflection_is_the_finding=True),
    ProofSpec("lockout", "a counted series of at least five FAILED "
              "authentication attempts on one endpoint - each carrying a "
              "credential field - none of them refused. The count is the "
              "evidence and the absence of a throttle is the bug",
              ("a counted series of failed authentication attempts is on "
               "record",
               "none of them was refused"),
              verify_no_throttle,
              floor=("a counted series of failed authentication attempts is "
                     "on record",),
              aliases=("no-rate-limit", "bruteforce", "no-lockout")),
    ProofSpec("websocket", "a 101 whose accept token answers the key this "
              "request sent, from an Origin the target does not own, and a "
              "frame the channel answered carrying the probe nonce",
              ("the handshake completed the RFC 6455 challenge",
               "accepted from an origin the target does not own",
               "the channel answered a message"),
              verify_websocket_channel,
              floor=("accepted from an origin the target does not own",
                     "the channel answered a message"),
              aliases=("cswsh", "ws"),
              notes="Grades the channel being open cross-origin. Data taken "
                    "over it is a different class and is graded as one.",
              reflection_is_the_finding=True),
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
