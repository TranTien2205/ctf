"""The proof matrix: what each vulnerability class must produce before it is a
finding rather than a guess.

The rule the whole system is built around:

    A scanner's label, a tool's confidence score, a template match, a timeout,
    a 500, a reflected payload and a plausible explanation are all *candidates*.
    A finding needs an observation that could not have happened if the
    vulnerability were absent.

For code execution that observation is the output of a benign command carrying
a nonce the target could not have known (`id; echo <nonce>`) — never a reverse
shell, never a write. For everything else it is the class-specific artifact in
the table below, and for every differential class it is the artifact **plus its
control**, because an asymmetry with no control is the most common way an
automated tester invents a vulnerability it did not find.

Grades:

    proven      the requirement is met, controls included
    supported   a class-specific signal exists, a control or nonce is missing
    unproven    nothing in the evidence meets the requirement
    refused     the class may not be proven by this system at all
"""
from __future__ import annotations

import json
import re
import secrets
from dataclasses import dataclass, field
from typing import Callable

NONCE_PREFIX = "argus"


def nonce(length: int = 10) -> str:
    """Unguessable, alphanumeric, greppable, safe in a URL and in a shell word."""
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    return NONCE_PREFIX + "".join(secrets.choice(alphabet) for _ in range(length))


def marker_command(token: str, os_family: str = "unix") -> str:
    """The only command this system runs to prove execution. Reads identity,
    echoes a nonce, changes nothing, opens no socket, leaves no artifact."""
    if os_family == "windows":
        return f"whoami & echo {token}"
    return f"id; echo {token}"


# --- evidence helpers --------------------------------------------------------

UID_RE = re.compile(r"uid=\d+\([^)]+\)")
WINID_RE = re.compile(r"(?i)\b(nt authority\\\\\w+|[\w.-]+\\\\[\w.$-]+)\b")
PASSWD_RE = re.compile(r"^[a-z_][a-z0-9_-]*:[^:]*:\d+:\d+:", re.MULTILINE)
WIN_INI_RE = re.compile(r"(?i)\[(fonts|extensions|mci extensions|boot loader)\]")
PRIVKEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")

FILE_SENTINELS = (
    ("unix /etc/passwd", PASSWD_RE),
    ("windows win.ini", WIN_INI_RE),
    ("private key", PRIVKEY_RE),
)


def _text_of(record: dict) -> str:
    """Everything in one evidence record a verifier may read as observed output."""
    parts = [
        record.get("stdout_span") or "",
        record.get("stderr_span") or "",
        ((record.get("response") or {}).get("body_span")) or "",
        str(((record.get("response") or {}).get("headers")) or ""),
        str(record.get("extracted") or ""),
        record.get("callback_payload") or "",
    ]
    return "\n".join(part for part in parts if part)


def _output_text(record: dict) -> str:
    """Only what the target SENT BACK.

    `_text_of` includes `str(record["extracted"])`, which is right for most
    verifiers and wrong for this one: a record whose `extracted` merely mentions
    its own nonce — an uploaded filename, a stored path, an unkeyed header value
    — satisfied "the nonce was echoed by the target" with nothing executed. A
    tool author worked around it by refusing to set `nonce` on a cache record and
    left a comment saying the next author would not know to. This is the fix that
    comment asked for.
    """
    response = record.get("response") or {}
    parts = [record.get("stdout_span") or "", record.get("stderr_span") or "",
             response.get("body_span") or "", record.get("callback_payload") or "",
             str(response.get("headers") or "")]
    return "\n".join(part for part in parts if part)


def _records_for(records: list[dict], *kinds: str) -> list[dict]:
    if not kinds:
        return list(records)
    return [r for r in records if (r.get("kind") or "probe") in kinds]


def _check(name: str, ok: bool, detail: str = "") -> dict:
    return {"check": name, "ok": bool(ok), "detail": detail}


def _grade(checks: list[dict], required: tuple[str, ...],
           veto: tuple[str, ...] = (), floor: tuple[str, ...] = ()) -> str:
    """`supported` means partial progress on the requirement itself.

    Only the required checks count. A hygiene check such as "extraction stayed
    minimal" passes trivially when nothing was extracted, and an early version of
    this function read that as partial evidence — so an untouched hypothesis came
    back `supported` and the controller sent the model to close a gap that was
    the whole vulnerability.
    """
    passed = {c["check"] for c in checks if c["ok"]}
    # A veto is not a requirement, it is a disqualification. "The proof command
    # stayed benign" must not *carry* a grade — it passes trivially when no
    # command ran at all, and as a required check it made any record whatsoever
    # under an rce hypothesis recordable as a critical candidate. As a veto it
    # does the job it was written for: a destructive request voids the evidence
    # and no grade above unproven is available.
    for name in veto:
        if name not in passed:
            return "unproven"
    # A floor check is the one that makes the evidence ABOUT this class at all.
    # Without it, a record set containing only the control graded `supported`:
    # "every redirect destination stayed in origin" came back as partial progress
    # towards an open redirect, and a cache probe that poisoned nothing came back
    # as a candidate. `supported` has to mean partial progress on the finding,
    # not partial progress on the paperwork.
    for name in floor:
        if name not in passed:
            return "unproven"
    if required and all(name in passed for name in required):
        return "proven"
    return "supported" if any(name in passed for name in required) else "unproven"


# --- verifiers ---------------------------------------------------------------

def verify_command_output(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Code execution. The nonce is the proof; the identity line is the context."""
    checks = []
    # A nonce alone is not a declaration. `http.probe` writes the caller's
    # `token` into the evidence record's `nonce` field, so a parameter that
    # merely REFLECTS the token satisfied "a nonce exists" and the whole class
    # graded `proven` with nothing executed — verified end to end against the
    # fixture's /search endpoint. The declaration is a nonce AND the marker
    # command that was sent with it.
    declaring = [r for r in records if r.get("nonce") and _command_text(r)]
    declared = {r.get("nonce") for r in declaring}
    checks.append(_check("benign marker command declared", bool(declaring),
                         f"nonces: {sorted(n for n in declared if n)}" if declaring else
                         "no record carries BOTH a nonce and the command that was sent; a "
                         "reflected token is not a declaration"))
    echoed, identity = None, None
    for record in records:
        text = _output_text(record)
        token = record.get("nonce")
        if token and token in text and _command_text(record):
            echoed = record
        if UID_RE.search(text) or WINID_RE.search(text):
            identity = record
    checks.append(_check("nonce echoed by the target", echoed is not None,
                         f"record {echoed.get('id')}" if echoed else
                         "the nonce does not appear in the output of any record that sent a "
                         "command"))
    checks.append(_check("identity output present", identity is not None,
                         (UID_RE.search(_output_text(identity))
                          or WINID_RE.search(_output_text(identity))).group(0)
                         if identity else
                         "no uid=/whoami line observed. This is the check a reflected payload "
                         "cannot pass: echoing `id; echo <nonce>` back as text does not produce "
                         "an identity line"))
    destructive = [r for r in records if _looks_destructive(r)]
    checks.append(_check("proof command stayed benign", not destructive,
                         "" if not destructive else
                         f"records {[r.get('id') for r in destructive]} ran more than a read"))
    return checks


_DESTRUCTIVE_RE = re.compile(
    r"(?i)\b(rm\s+-rf|mkfs|dd\s+if=|shutdown|reboot|:\(\)\s*\{|useradd|net\s+user\s+\S+\s+/add|"
    r"nc\s+-e|bash\s+-i|/dev/tcp/|certutil\s+-urlcache|invoke-webrequest\s+-outfile|chmod\s+777\s+/)\b"
)


def _command_text(record: dict) -> str:
    """What this record says it sent, as one string. Empty when it sent nothing."""
    command = record.get("command")
    if isinstance(command, list):
        return " ".join(str(part) for part in command)
    return str(command or "")


def _looks_destructive(record: dict) -> bool:
    text = _command_text(record)
    payload = str(((record.get("request") or {}).get("body")) or "") + " " \
        + str(record.get("payload") or "") + " " + str((record.get("request") or {}).get("url") or "")
    return bool(_DESTRUCTIVE_RE.search(text + " " + payload))


def verify_data_extraction(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Injection into a data store. A named table and at least one real row."""
    checks = []
    banner, table, rows = None, None, 0
    for record in records:
        extracted = record.get("extracted") or {}
        if extracted.get("dbms") or extracted.get("version"):
            banner = extracted.get("dbms") or extracted.get("version")
        if extracted.get("table"):
            count = extracted.get("row_count")
            if count is None:
                count = len(extracted.get("rows") or [])
            if count and count > rows:
                table, rows = extracted.get("table"), count
    checks.append(_check("data store fingerprinted", bool(banner), str(banner or "no dbms/version reported")))
    checks.append(_check("named table read", bool(table), f"{table}" if table else "no table named in evidence"))
    checks.append(_check("at least one row returned", rows >= 1, f"{rows} row(s)"))
    scoped = [r for r in records if (r.get("extracted") or {}).get("rows")]
    bounded = bool(scoped) and all(_rows_are_bounded(r) for r in scoped)
    checks.append(_check("extraction stayed minimal", bounded,
                         "" if bounded else ("nothing was extracted, so there is nothing to judge"
                                             if not scoped else
                                             "a dump larger than the proof was taken")))
    return checks


def _rows_are_bounded(record: dict, limit: int = 5) -> bool:
    rows = (record.get("extracted") or {}).get("rows") or []
    return len(rows) <= limit


def verify_file_read(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Arbitrary read. A sentinel from a file whose contents are known, plus the
    control that a path which does not exist answers differently."""
    checks, hit, control = [], None, None
    for record in records:
        text = _text_of(record)
        for label, pattern in FILE_SENTINELS:
            if pattern.search(text):
                hit = (label, record)
                break
        if (record.get("kind") == "control") or record.get("is_control"):
            control = record
    checks.append(_check("known-file sentinel observed", hit is not None,
                         f"{hit[0]} in record {hit[1].get('id')}" if hit else
                         "no /etc/passwd, win.ini or private-key signature in any response"))
    checks.append(_check("negative control recorded", control is not None,
                         f"record {control.get('id')}" if control else
                         "no request for a non-existent path to compare against"))
    return checks


def verify_oob(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Blind classes. The target reached a collector we control, carrying a nonce."""
    checks = []
    declared = {r.get("nonce") for r in records if r.get("nonce")}
    callbacks = [r for r in records if (r.get("kind") == "oob")]
    matched = [r for r in callbacks if r.get("nonce") in declared and r.get("nonce")]
    internal = [r for r in records if (r.get("extracted") or {}).get("internal_evidence")]
    checks.append(_check("probe carried a unique collector token", bool(declared),
                         f"{sorted(n for n in declared if n)}" or ""))
    checks.append(_check("collector observed the callback", bool(matched),
                         f"from {[r.get('source_ip') or r.get('target') for r in matched]}" if matched
                         else "no interaction recorded for the token"))
    checks.append(_check("or an internal-only response was returned", bool(internal),
                         str([(r.get("extracted") or {}).get("internal_evidence") for r in internal])
                         if internal else "not applicable"))
    return checks


def verify_differential(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Authorization, race and cache classes. Two actors or two orderings, and
    the control that establishes what the outcome should have been."""
    checks = []
    # The identities in play are the actors AND the subjects they reached, plus any
    # declared ordering. In a real IDOR the actor does not change — alice stays
    # alice — and what changes is whose record she reads. An earlier version
    # counted actors only, so a textbook IDOR failed its own requirement.
    identities = {r.get("actor") for r in records if r.get("actor")}
    identities |= {r.get("accessed_subject") for r in records if r.get("accessed_subject")}
    identities |= {r.get("ordering") for r in records if r.get("ordering")}
    controls = [r for r in records if r.get("kind") == "control" or r.get("is_control")]
    probes = [r for r in records if r not in controls]
    outcomes = {(r.get("response") or {}).get("status") for r in records if r.get("response")}
    cross = [r for r in probes if r.get("accessed_subject") and r.get("actor")
             and r.get("accessed_subject") != r.get("actor")]
    checks.append(_check("two distinct actors or orderings", len(identities) >= 2,
                         f"identities: {sorted(i for i in identities if i)}"))
    checks.append(_check("one actor reached another's subject", bool(cross),
                         f"{[(r.get('actor'), r.get('accessed_subject')) for r in cross]}" if cross
                         else "no record names both the actor and whose data it read"))
    checks.append(_check("control recorded for the expected outcome", bool(controls),
                         f"record {controls[0].get('id')}" if controls else
                         "no control request, so the asymmetry proves nothing"))
    checks.append(_check("outcomes actually differ", len(outcomes) >= 2, f"statuses: {sorted(s for s in outcomes if s)}"))
    return checks


def verify_off_origin_redirect(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Open redirect. The Location is the measurement, not the status.

    `verify_differential` was wrong for this class in both directions: a textbook
    redirector answers the same 302 to an in-origin and an off-origin
    destination, so "outcomes actually differ" made a real finding `unproven` —
    and a status difference with an in-origin Location made a non-finding
    `proven`.
    """
    checks = []
    off = [r for r in records
           if (r.get("extracted") or {}).get("off_origin_location")
           or (r.get("extracted") or {}).get("off_origin_via")]
    redirecting = [r for r in off if ((r.get("response") or {}).get("status") or 0) // 100 == 3]
    controls = [r for r in records if r.get("kind") == "control" or r.get("is_control")]
    in_origin_control = [r for r in controls
                         if not (r.get("extracted") or {}).get("off_origin_location")]
    checks.append(_check("the Location points off origin", bool(redirecting),
                         str([(r.get("extracted") or {}).get("off_origin_location")
                              for r in redirecting]) if redirecting else
                         "no 3xx response carries a Location outside the request origin"))
    checks.append(_check("the shape that got through is named", bool(
        [r for r in redirecting if (r.get("extracted") or {}).get("shape")]),
        str([(r.get("extracted") or {}).get("shape") for r in redirecting])
        if redirecting else "the encoding that defeated the filter is what a fix has to cover"))
    checks.append(_check("control recorded for the expected outcome", bool(in_origin_control),
                         f"record {in_origin_control[0].get('id')}" if in_origin_control else
                         "no in-origin destination on record, so nothing shows the parameter is "
                         "honoured at all"))
    return checks


def verify_cache_poisoning(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """A poisoned cache is proven by the SECOND request, not the first.

    `verify_differential` graded this class `supported` on the clean control
    alone, so a probe that found nothing but took its control was recordable as a
    candidate.
    """
    checks = []
    clean_after = [r for r in records if r.get("ordering") == "clean-requester-after"]
    reached = [r for r in clean_after
               if (r.get("extracted") or {}).get("nonce_in_clean_response")]
    controls = [r for r in records if r.get("ordering") == "clean-requester-before"
                or r.get("is_control")]
    poisoning = [r for r in records if r.get("ordering") == "poisoning-requester"]
    cache_seen = [r for r in records if (r.get("extracted") or {}).get("cache_headers")]
    checks.append(_check("the value reached a requester that did not send it", bool(reached),
                         f"record {reached[0].get('id')}" if reached else
                         "the value never came back to a clean fetch, so nothing was poisoned"))
    checks.append(_check("clean control recorded", bool(controls),
                         f"record {controls[0].get('id')}" if controls else
                         "no clean fetch before the poisoning request"))
    checks.append(_check("the poisoning request is on record", bool(poisoning),
                         "" if poisoning else "nothing shows what put the value in the cache"))
    checks.append(_check("a cache was observed at all", bool(cache_seen),
                         "" if cache_seen else "no cache headers in any record: this may be an "
                                               "unkeyed input with no cache behind it"))
    return checks


def verify_ordering_differential(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Race conditions. Two orderings of the same requests, and the difference may
    be one of DEGREE rather than of status: same statuses, more successes in
    parallel. A status-only comparison cannot see that, which is the usual shape
    of a limit overrun."""
    checks = []
    orderings = {r.get("ordering") for r in records if r.get("ordering")}
    controls = [r for r in records if r.get("kind") == "control" or r.get("is_control")]
    statuses = {(r.get("response") or {}).get("status") for r in records if r.get("response")}
    distributions = [((r.get("extracted") or {}).get("distribution") or {}) for r in records]
    surplus = [(r.get("extracted") or {}).get("surplus_successes") for r in records
               if (r.get("extracted") or {}).get("surplus_successes") is not None]
    distinct = {json.dumps(d, sort_keys=True) for d in distributions if d}
    differs = (len(distinct) >= 2 or any((value or 0) > 0 for value in surplus)
               or len({s for s in statuses if s is not None}) >= 2)
    checks.append(_check("two orderings on record", len(orderings) >= 2,
                         f"orderings: {sorted(o for o in orderings if o)}"))
    checks.append(_check("serial control recorded", bool(controls),
                         f"record {controls[0].get('id')}" if controls else
                         "without the serial ordering, a burst is a story about a flaky endpoint"))
    checks.append(_check("the orderings reached different outcomes", differs,
                         (f"surplus successes: {surplus}" if surplus else
                          (f"distributions: {sorted(distinct)[:2]}" if distinct else
                           f"statuses: {sorted(s for s in statuses if s is not None)}")) if differs else
                         "same statuses and the same distribution in both orderings: this is "
                         "flakiness, or no window at all"))
    checks.append(_check("statuses differ as well", len(statuses) >= 2,
                         "" if len(statuses) >= 2 else "reported for context: an overrun of "
                                                       "degree does not change the status"))
    return checks


def verify_browser_execution(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Client-side execution. Reflection is not execution; a browser says so."""
    checks = []
    declared = {r.get("nonce") for r in records if r.get("nonce")}
    browser = [r for r in records if r.get("kind") == "browser"]
    executed = [r for r in browser if r.get("executed") and (r.get("nonce") in declared)]
    reflected = [r for r in records if r.get("reflected_context")]
    checks.append(_check("payload reflected into an executable context", bool(reflected),
                         str([r.get("reflected_context") for r in reflected]) if reflected else
                         "no record names the parse context the payload landed in"))
    checks.append(_check("a real browser executed it", bool(executed),
                         f"record {executed[0].get('id')}" if executed else
                         "no headless-browser record with executed=true and the probe nonce"))
    return checks


def verify_template_eval(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Server-side template/expression injection. The expression must be gone and
    its result present; a page that echoes `{{7*7}}` back has proven nothing."""
    checks = []
    hit = None
    for record in records:
        expression = str(record.get("payload") or "")
        expected = str((record.get("extracted") or {}).get("expected_result") or "")
        text = _text_of(record)
        # Uniqueness is part of this check, not a separate one. As its own check it
        # passed on the probe's shape alone — a four-digit expected result makes it
        # true even when nothing was evaluated — so a page that echoed the
        # expression back came out `supported` instead of `unproven`.
        if (expected and len(expected) >= 4 and expected in text
                and expression and expression not in text):
            hit = record
            break
    checks.append(_check("expression evaluated, not echoed", hit is not None,
                         f"record {hit.get('id')}" if hit else
                         "no record shows a result of four digits or more without the literal "
                         "expression; a short result such as 49 can appear by chance, so use a "
                         "nonce-derived product"))
    echoed = [r for r in records if str(r.get("payload") or "")
              and str(r.get("payload")) in _text_of(r)]
    checks.append(_check("payload was not merely reflected", not echoed,
                         "" if not echoed else
                         f"records {[r.get('id') for r in echoed]} echo the expression verbatim"))
    return checks


def verify_state_change(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Business-logic and CSRF classes. Read, act, read again — and the actor who
    acted must be one that should not have been able to."""
    checks = []
    before = [r for r in records if r.get("phase") == "before"]
    action = [r for r in records if r.get("phase") == "action"]
    after = [r for r in records if r.get("phase") == "after"]
    changed = bool(before and after and _text_of(before[0]) != _text_of(after[0]))
    checks.append(_check("state read before the action", bool(before)))
    checks.append(_check("action performed and recorded", bool(action)))
    checks.append(_check("state read after, and it differs", changed,
                         "" if changed else "the two reads are identical, so nothing changed"))
    unauthorised = any(r.get("actor") and r.get("actor") != r.get("owner") for r in action)
    checks.append(_check("the acting identity should not have been able to", unauthorised,
                         "" if unauthorised else "no record distinguishes the actor from the owner"))
    return checks


def verify_token_forgery(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """JWT/session classes. A token we minted is accepted, and a broken one is not."""
    checks = []
    accepted = [r for r in records if r.get("token_accepted")]
    rejected = [r for r in records if r.get("token_accepted") is False]
    privileged = [r for r in accepted if r.get("privileged_marker")]
    checks.append(_check("forged token accepted", bool(accepted),
                         f"record {accepted[0].get('id')}" if accepted else "no accepted forged token"))
    checks.append(_check("a deliberately invalid token is rejected", bool(rejected),
                         "" if rejected else "without this control, the endpoint may need no token at all"))
    checks.append(_check("privileged content returned", bool(privileged),
                         str([r.get("privileged_marker") for r in privileged]) if privileged else
                         "acceptance alone does not show a privilege gain"))
    return checks


def verify_secret_leak(records: list[dict], spec: "ProofSpec") -> list[dict]:
    """Exposed credential. Present in a response, and shown to be live — against
    the issuing service, never against a third party outside the engagement."""
    checks = []
    found = [r for r in records if (r.get("extracted") or {}).get("secret_kind")]
    validated = [r for r in found if (r.get("extracted") or {}).get("validated") is True]
    # `all()` over an empty list is True, which made this hygiene check pass on a
    # record with no secret in it at all — and since it is a required check, any
    # record under a secret-exposure hypothesis graded `supported`.
    redacted = bool(found) and all(
        "REDACTED" in str((r.get("extracted") or {}).get("secret_value", "REDACTED"))
        or len(str((r.get("extracted") or {}).get("secret_value", ""))) <= 8 for r in found)
    checks.append(_check("secret observed in a response", bool(found),
                         str([(r.get("extracted") or {}).get("secret_kind") for r in found])))
    checks.append(_check("secret shown to be live", bool(validated),
                         "" if validated else "not validated, so severity is a hypothesis"))
    checks.append(_check("secret stored redacted", redacted,
                         "" if redacted else ("no secret was observed, so there is nothing to "
                                              "judge" if not found else
                                              "the full secret was written into the ledger")))
    return checks


def verify_refused(records: list[dict], spec: "ProofSpec") -> list[dict]:
    return [_check("class is provable by this system", False, spec.refusal or "refused")]


# --- the matrix --------------------------------------------------------------

@dataclass(frozen=True)
class ProofSpec:
    vuln_class: str
    kind: str
    severity: str
    requirement: str
    required_checks: tuple[str, ...]
    verifier: Callable[[list[dict], "ProofSpec"], list[dict]]
    veto_checks: tuple[str, ...] = ()
    floor_checks: tuple[str, ...] = ()
    benign_proof: str | None = None
    aliases: tuple[str, ...] = ()
    refusal: str | None = None
    notes: str = ""

    def verify(self, records: list[dict]) -> "ProofVerdict":
        records = list(records or [])
        if self.verifier is not verify_refused and not records:
            return ProofVerdict(self.vuln_class, self.kind, "unproven",
                                [_check("evidence exists", False, "no evidence record is attached")],
                                ["evidence exists"], self.requirement)
        checks = self.verifier(records, self)
        grade = ("refused" if self.verifier is verify_refused
                 else _grade(checks, self.required_checks, self.veto_checks, self.floor_checks))
        missing = [c["check"] for c in checks if not c["ok"]
                   and c["check"] in (*self.required_checks, *self.veto_checks,
                                      *self.floor_checks)]
        return ProofVerdict(self.vuln_class, self.kind, grade, checks, missing, self.requirement)


@dataclass
class ProofVerdict:
    vuln_class: str
    kind: str
    grade: str
    checks: list[dict] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    requirement: str = ""

    @property
    def proven(self) -> bool:
        return self.grade == "proven"

    def to_dict(self) -> dict:
        return {
            "vuln_class": self.vuln_class, "kind": self.kind, "grade": self.grade,
            "checks": self.checks, "missing": self.missing, "requirement": self.requirement,
        }

    def explain(self) -> str:
        lines = [f"{self.vuln_class}: {self.grade} ({self.kind})"]
        for check in self.checks:
            lines.append(f"  [{'x' if check['ok'] else ' '}] {check['check']}"
                         + (f" — {check['detail']}" if check.get("detail") else ""))
        if self.missing:
            lines.append(f"  missing: {', '.join(self.missing)}")
        return "\n".join(lines)


def _spec(*args, **kwargs) -> ProofSpec:
    return ProofSpec(*args, **kwargs)


# The identity line is what a reflection cannot fake. "Proof command stayed
# benign" moved to the veto set: it disqualifies, it does not qualify.
RCE_REQUIRED = ("benign marker command declared", "nonce echoed by the target",
                "identity output present")
RCE_VETO = ("proof command stayed benign",)
# A SQL injection proof names the engine as well as the data: the fingerprint is
# what separates "this parameter reaches a database" from "this page echoes text".
SQLI_REQUIRED = ("data store fingerprinted", "named table read", "at least one row returned")
# A document store or a GraphQL endpoint may not report a version at all, so the
# fingerprint is not required there.
EXTRACTION_REQUIRED = ("named table read", "at least one row returned")

MATRIX: dict[str, ProofSpec] = {}


def _register(spec: ProofSpec) -> None:
    MATRIX[spec.vuln_class] = spec
    for alias in spec.aliases:
        MATRIX[alias] = spec


for _spec_obj in [
    _spec("rce", "command_output", "critical",
          "the output of `id; echo <nonce>` returned by the target, with the nonce matching the probe",
          RCE_REQUIRED, verify_command_output, veto_checks=RCE_VETO,
          benign_proof="id; echo <nonce>",
          aliases=("command-injection", "os-command-injection", "code-injection"),
          notes="No shell, no payload download, no persistence. The nonce is the proof."),
    _spec("deserialization", "command_output", "critical",
          "code execution proven the same way as rce, from a serialized payload",
          RCE_REQUIRED, verify_command_output, veto_checks=RCE_VETO,
          benign_proof="id; echo <nonce>",
          aliases=("insecure-deserialization", "pickle", "java-deserialization")),
    _spec("file-upload-rce", "command_output", "critical",
          "the uploaded file executed, proven by the nonce in its output",
          RCE_REQUIRED, verify_command_output, veto_checks=RCE_VETO,
          benign_proof="id; echo <nonce>",
          aliases=("unrestricted-file-upload",),
          notes="Upload one file, named with the nonce, and delete it in the cleanup step."),
    _spec("ssti", "template_eval", "high",
          "a nonce-derived arithmetic result rendered by the template engine, with the expression absent",
          ("expression evaluated, not echoed",),
          verify_template_eval, aliases=("template-injection", "el-injection", "expression-injection")),
    _spec("sqli", "data_extraction", "critical",
          "the DBMS fingerprint plus at least one row from a named table, bounded to what proves the read",
          SQLI_REQUIRED, verify_data_extraction,
          aliases=("sql-injection", "blind-sqli", "second-order-sqli"),
          notes="Five rows is a proof. A full dump is an incident."),
    _spec("nosqli", "data_extraction", "high",
          "documents returned from a named collection that the query should not have reached",
          EXTRACTION_REQUIRED, verify_data_extraction, aliases=("nosql-injection", "mongo-injection")),
    _spec("graphql-exposure", "data_extraction", "medium",
          "introspection or a batched query returning records outside the caller's scope",
          EXTRACTION_REQUIRED, verify_data_extraction, aliases=("graphql",)),
    _spec("lfi", "file_read", "high",
          "a sentinel from a file whose contents are known, plus a control path that does not exist",
          ("known-file sentinel observed", "negative control recorded"), verify_file_read,
          floor_checks=("known-file sentinel observed",),
          aliases=("path-traversal", "arbitrary-file-read", "directory-traversal")),
    _spec("xxe", "file_read", "high",
          "a local file read through the parser, or a collector callback for the blind case",
          ("known-file sentinel observed",), verify_file_read, aliases=("xml-external-entity",)),
    _spec("ssrf", "oob", "high",
          "a callback at our collector carrying the probe nonce, or a response only the internal network could give",
          ("probe carried a unique collector token", "collector observed the callback"), verify_oob,
          aliases=("server-side-request-forgery", "blind-ssrf")),
    _spec("log4shell", "oob", "critical",
          "a JNDI lookup reaching our collector with the probe nonce",
          ("probe carried a unique collector token", "collector observed the callback"), verify_oob,
          aliases=("jndi-injection",)),
    _spec("idor", "differential", "high",
          "actor A reading actor B's subject, with the control showing A is not entitled to it",
          ("two distinct actors or orderings", "one actor reached another's subject",
           "control recorded for the expected outcome", "outcomes actually differ"),
          verify_differential, floor_checks=("one actor reached another's subject",),
          aliases=("bola", "authorization-bypass", "broken-access-control")),
    _spec("auth-bypass", "token_forgery", "critical",
          "a forged or absent credential accepted on a privileged resource, with an invalid one rejected",
          ("forged token accepted", "a deliberately invalid token is rejected",
           "privileged content returned"),
          verify_token_forgery, floor_checks=("forged token accepted",),
          aliases=("jwt", "jwt-forgery", "session-fixation", "mfa-bypass")),
    _spec("race-condition", "differential", "high",
          "an outcome impossible under serial execution, with the serial control recorded; the "
          "difference may be one of degree — the same statuses and more successes in parallel",
          ("two orderings on record", "serial control recorded",
           "the orderings reached different outcomes"), verify_ordering_differential,
          floor_checks=("the orderings reached different outcomes",),
          aliases=("toctou", "limit-overrun")),
    _spec("cache-poisoning", "differential", "high",
          "a value only the poisoning request sent, returned to a requester that did not send it, "
          "with the clean control",
          ("the value reached a requester that did not send it", "clean control recorded"),
          verify_cache_poisoning,
          floor_checks=("the value reached a requester that did not send it",),
          aliases=("web-cache-deception", "request-smuggling")),
    _spec("xss", "browser_execution", "medium",
          "a headless browser executing the payload and reporting the probe nonce",
          ("payload reflected into an executable context", "a real browser executed it"),
          verify_browser_execution, aliases=("reflected-xss", "stored-xss", "dom-xss")),
    _spec("prototype-pollution", "browser_execution", "medium",
          "a polluted property observably changing behaviour in a browser or a server response",
          ("a real browser executed it",), verify_browser_execution),
    _spec("csrf", "state_change", "medium",
          "a cross-origin request changing state, read back afterwards, by an actor who is not the owner",
          ("state read before the action", "action performed and recorded",
           "state read after, and it differs", "the acting identity should not have been able to"),
          verify_state_change, aliases=("business-logic", "mass-assignment", "logic-flaw")),
    _spec("secret-exposure", "secret_leak", "high",
          "the credential observed in a response and shown to be live against its own issuer",
          ("secret observed in a response", "secret shown to be live",
           "secret stored redacted"), verify_secret_leak,
          aliases=("info-disclosure", "source-leak", "credential-leak")),
    _spec("open-redirect", "differential", "low",
          "a 3xx Location pointing off origin, with the in-origin control showing the destination "
          "parameter is honoured",
          ("the Location points off origin", "control recorded for the expected outcome"),
          verify_off_origin_redirect, floor_checks=("the Location points off origin",)),
    _spec("dos", "refused", "n/a",
          "this system does not prove availability impact",
          (), verify_refused,
          refusal="Denial of service is out of scope by construction: the proof is the damage. "
                  "Report the mechanism from source or configuration instead, with no load generated.",
          aliases=("ddos", "resource-exhaustion", "zip-bomb")),
]:
    _register(_spec_obj)

CANDIDATE_ONLY = {
    "nuclei-match": "A template match names a candidate class. Re-verify under that class's requirement.",
    "nikto-finding": "A signature hit is a candidate. Re-verify under the class it implies.",
    "version-cve": "A version banner implies a CVE; exploitability is proven, not inferred.",
}


def spec_for(vuln_class: str) -> ProofSpec | None:
    return MATRIX.get((vuln_class or "").strip().lower())


def classes() -> list[str]:
    return sorted({spec.vuln_class for spec in MATRIX.values()})


def verify(vuln_class: str, records: list[dict]) -> ProofVerdict:
    spec = spec_for(vuln_class)
    if spec is None:
        hint = CANDIDATE_ONLY.get((vuln_class or "").lower())
        return ProofVerdict(vuln_class, "unknown", "unproven", [
            _check("class is in the proof matrix", False,
                   hint or f"no requirement defined for {vuln_class!r}; add one before claiming it")
        ], ["class is in the proof matrix"], hint or "")
    return spec.verify(records)
