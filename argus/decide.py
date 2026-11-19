"""The next action, computed from the session's own recorded evidence.

Ported from the ledger plane of the four-plane tree, rebuilt on this tree's
artifacts instead of a second state file. The property worth porting is not the
file format; it is this one:

    the next move is computed from what was recorded, so it does not drift
    with the conversation.

A strong model given a transcript and an open question usually picks a sensible
next probe. A tired one, or one whose context has rolled over, instead re-sends
the last payload with a new separator, or writes a confident paragraph about a
bug it never showed. From outside the two are indistinguishable - unless the
next action is derived from the bytes on disk, which is what this module does.

Every rule is ordered, fail-closed, and names the observation that triggered
it. Nothing here invents a target, a parameter or a class: each rule cites
request ids, a finding id or a proof-matrix requirement. Rule 7 is the only
one that says stop.

Two readers:

* the operator, via `argus next <session>` - a second opinion that cannot be
  talked round, because it never saw the conversation;
* the agent itself, via the `next_action` tool - so "what does the evidence
  say to do" is a question it can ask rather than a thing it must remember.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

from . import proof

# A probe tool whose name does not say which class it tests is not evidence
# that the class was tried. These are the ones that do.
PROBE_CLASS = {
    "probe_sqli": "sqli", "probe_nosqli": "nosqli", "probe_cmdi": "rce",
    "probe_reflection": "xss", "probe_ssti": "ssti", "probe_ssrf": "ssrf",
    # The out-of-band half of the same class. Attributed to `ssrf` and not
    # excluded: it records a request against the endpoint like any probe, so
    # a ledger that could not see it would read the class as never tried
    # however often the callback probe ran - and this is the call that
    # produces the artifact `proven` needs, so it is the one that must count.
    "probe_ssrf_oob": "ssrf",
    "probe_lfi": "lfi", "probe_idor": "idor", "probe_redirect": "redirect",
    "probe_xxe": "xxe", "probe_deserialize": "deserialize",
    "probe_cors": "cors", "probe_csrf": "csrf", "probe_cache": "cache",
    "probe_xfh": "xfh", "probe_massassign": "massassign",
    "probe_lockout": "lockout", "probe_enum": "enum",
    "probe_upload": "upload", "probe_crlf": "crlf",
    "probe_method": "method", "probe_race": "race",
    "probe_smuggle": "smuggle", "probe_ppoll": "ppoll",
    "probe_websocket": "websocket", "probe_disclosure": "disclosure",
    # Not named `probe_*`, but it names its class and it sends: the
    # introspection query and the GET fallback are both tagged
    # `graphql_introspect`, so they ARE evidence the class was tried. They
    # were attributed to nothing, which cost three separate things - the
    # per-class budget never counted them, rule 6 never offered their
    # evidence for grading, and `_tool_for_class("graphql")` fell through to
    # `http_request`. A run could call it five times and the ledger would
    # still say graphql had never been probed, which is exactly the drift
    # this module exists to prevent.
    "graphql_introspect": "graphql",
}

# What to reach for FIRST on a class whose proof needs a chain this
# controller cannot name as one probe. Recommendations only, never
# evidence: `jwt_decode` and `jwt_forge` send nothing, so putting them in
# PROBE_CLASS would mark the class tried on an offline call - the same
# reason `fingerprint` is not in there. The ledger used to answer
# `http_request` here, which is the last step of the chain with no hint
# that the first two exist.
CLASS_TOOL_CHAIN = {
    "jwt": ("jwt_decode", "jwt_forge", "http_request"),
}
# Probe tools that must NOT be attributed to a class, and why. This is the
# other half of PROBE_CLASS, and it is data rather than a comment because
# the pair is a partition: every registered `probe_*` tool belongs to
# exactly one of the two, and a test holds that. PROBE_CLASS was only ever
# checked in the direction "every mapping names a real tool", which is the
# direction that cannot fail by neglect. The one that can is a new probe
# landing in the registry and being attributed to nothing - which is what
# happened to `graphql_introspect`, and the comment above records the three
# things it cost. Adding the entry fixed that instance; this partition is
# what makes the next one fail loudly instead.
UNATTRIBUTED_PROBES = {
    "probe_time": "a latency measurement is consistent with sqli, with rce, "
                  "and with a slow database. Recording it as 'this class was "
                  "tested' would let a timing run stand in for a proof it "
                  "cannot produce.",
}
# The same reasoning excludes the recon tools - mapping `fingerprint` to a
# class would make reading a banner count as probing - but they are not
# named `probe_*`, so the partition does not reach them.

# Probes worth reaching for on a parameterised endpoint nothing has tested.
# Ordered cheapest-and-most-likely first; this is a reading order, not a
# promise that any of them will find something.
_FIRST_PASS = ("probe_sqli", "probe_reflection", "probe_cmdi", "probe_ssti",
               "probe_lfi", "probe_redirect", "probe_ssrf")

# How many recorded REQUESTS against one class on one endpoint before the
# ledger says park it. The unit matters and was wrong: this counted requests
# while being documented as probes, and one `probe_sqli` call records about
# eleven - so a single call spent 220% of the budget and rule 5 recommended
# parking a class nobody had finished trying. The system prompt's guidance is
# ~5 probe calls, so the budget is that many calls' worth of requests.
#
# 12 is a BUDGETING figure and not a measurement of any probe, which is why
# nothing printed to an operator divides by it any more. Measured against
# the lab, requests recorded per single call: probe_reflection 1, probe_cmdi
# 3, probe_redirect 3, probe_ssti 8, probe_lfi 8, probe_sqli 11, probe_ssrf
# 11 - a 1-to-11 spread across 26 probes. So this budget is between 5 and 60
# calls depending on the probe, and a call count derived from it was wrong by
# up to 12x in either direction. The transcript carries no call boundary (an
# entry has chain, id, request, response, tool, ts), so the honest answer is
# that calls are not derivable from the record at all - only requests are.
REQUESTS_PER_PROBE = 12
PROBE_CALLS_PER_CLASS = 5
BUDGET_PER_CLASS = REQUESTS_PER_PROBE * PROBE_CALLS_PER_CLASS

_STATIC_RE = re.compile(
    r"\.(?:css|js|mjs|map|png|jpe?g|gif|svg|ico|woff2?|ttf|eot|webp|avif|"
    r"mp4|webm|pdf|zip|gz)(?:$|\?)", re.I)


def _reviewed(finding: dict) -> bool:
    """Has a model from another family read this finding's evidence?

    Reads the HISTORY first, the same way the markdown renderer does, so a
    finding judged once is not asked for again. A verdict that carries an
    `error` is NOT a review: the judge was asked and could not answer (no
    credential, a refusal, a timeout), and treating a failed call as a
    completed check is how an unchecked finding would look checked.
    """
    history = [v for v in (finding.get("judges") or []) if isinstance(v, dict)]
    if not history and isinstance(finding.get("judge"), dict):
        history = [finding["judge"]]
    return any(not v.get("error") for v in history)


@dataclass
class Action:
    """One computed next move. `why` always names the observation."""
    action: str
    why: str
    target: str = ""
    vuln_class: str = ""
    tool: str = ""
    finding_id: str = ""
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        out = {"action": self.action, "why": self.why}
        for key in ("target", "vuln_class", "tool", "finding_id"):
            if getattr(self, key):
                out[key] = getattr(self, key)
        if self.detail:
            out["detail"] = self.detail
        return out

    def render(self) -> str:
        bits = " ".join(f"{k}={v}" for k, v in self.to_dict().items()
                        if k not in ("action", "why", "detail"))
        lines = [f"NEXT: {self.action}" + (f"  {bits}" if bits else ""),
                 f"why: {self.why}"]
        for key, value in (self.detail or {}).items():
            rendered = json.dumps(value, ensure_ascii=False, default=str)
            lines.append(f"  {key}: {rendered[:400]}")
        return "\n".join(lines)


# --- reading the session ----------------------------------------------------

def _load_transcript(sdir: Path, cap: int = 4000) -> list[dict]:
    """Every recorded entry, newest-last. A malformed line is skipped, not
    fatal: a truncated tail is a fact about the run, not a reason to refuse to
    advise on the rest of it."""
    path = Path(sdir) / "transcript.jsonl"
    out: list[dict] = []
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if isinstance(entry, dict):
                    out.append(entry)
    except OSError:
        return []
    return out[-cap:]


def _load_findings(sdir: Path) -> list[dict]:
    try:
        data = json.loads((Path(sdir) / "findings.json").read_text(
            encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if isinstance(data, dict):
        data = data.get("findings")
    if not isinstance(data, (list, tuple)):
        # `findings.json` holding `42` raised TypeError: not iterable. The
        # contract is that a malformed file is a FACT about the run, not a
        # crash in the reader, and "malformed" covers a well-formed JSON
        # document of the wrong shape as much as a bad one.
        return []
    return [f for f in data if isinstance(f, dict)]


def _exchanges(entries: list[dict]) -> list[dict]:
    return [e for e in entries if isinstance(e.get("response"), dict)]


def _shape_of_url(url: str) -> str:
    """The endpoint key for a URL string, as `_endpoint` makes one."""
    parts = urlparse(str(url or ""))
    if not parts.netloc:
        return ""
    return f"{parts.scheme}://{parts.netloc}{parts.path or '/'}"


def _endpoint(entry: dict) -> str:
    url = str((entry.get("request") or {}).get("url") or "")
    parts = urlparse(url)
    if not parts.netloc:
        return ""
    return f"{parts.scheme}://{parts.netloc}{parts.path or '/'}"


def _params(entry: dict) -> set[str]:
    """Named inputs this request carried: query, form body, and the cookie
    names. A path segment is an input too, but naming one requires guessing
    which segment is data, so it is left to the operator."""
    req = entry.get("request") or {}
    url = str(req.get("url") or "")
    names = {k for k, _ in parse_qsl(urlparse(url).query, keep_blank_values=True)}
    body = req.get("body")
    if isinstance(body, str) and _looks_like_a_form(body):
        names |= {k for k, _ in parse_qsl(body, keep_blank_values=True)}
    return {n for n in names if _PARAM_NAME_RE.fullmatch(n)}


# A form field name, as opposed to whatever `parse_qsl` makes of arbitrary
# text containing "=". `'=' in body` admitted XML prologs, SQL and multipart
# preambles, so the ledger recommended probing parameters called
# `<?xml version` and `SELECT 1 FROM t WHERE a`. Found by an audit.
_PARAM_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.\[\]-]{0,63}")


def _looks_like_a_form(body: str) -> bool:
    """Is this a urlencoded form body, rather than text that has an "=" in it?

    Cheap and strict: no markup, no JSON, no multipart preamble, and every
    pair has to be `name=value` with a plausible name.
    """
    head = body.lstrip()[:1]
    if not body or "=" not in body or head in ("<", "{", "[", "-"):
        return False
    if "\r\n" in body or "\n" in body:
        return False                      # a form body is one line
    pairs = parse_qsl(body, keep_blank_values=True)
    if not pairs:
        return False
    return all(_PARAM_NAME_RE.fullmatch(k) for k, _ in pairs)


def _tool_of(entry: dict) -> str:
    return str(entry.get("tool") or entry.get("via") or "")


def _probes_run(entries: list[dict]) -> dict[tuple[str, str], int]:
    """(endpoint, class) -> how many probe requests landed on it."""
    counts: dict[tuple[str, str], int] = {}
    for entry in entries:
        klass = PROBE_CLASS.get(_tool_of(entry))
        if not klass:
            continue
        endpoint = _endpoint(entry)
        if not endpoint:
            continue
        counts[(endpoint, klass)] = counts.get((endpoint, klass), 0) + 1
    return counts


def _by_id(entries: list[dict]) -> dict[str, dict]:
    return {str(e.get("id")): e for e in entries if e.get("id")}


def _surface(entries: list[dict]) -> dict[str, set[str]]:
    """Parameterised endpoints seen in the transcript -> their input names.

    An endpoint with no named input is not surface this module will recommend
    probing: there is nothing to put a payload in, and recommending one anyway
    is how a ledger starts inventing work.
    """
    out: dict[str, set[str]] = {}
    for entry in _exchanges(entries):
        endpoint = _endpoint(entry)
        if not endpoint or _STATIC_RE.search(endpoint):
            continue
        names = _params(entry)
        if not names:
            continue
        out.setdefault(endpoint, set()).update(names)
    return out


# --- the rules --------------------------------------------------------------

def next_action(sdir: Path | str, *, max_scan: int = 150) -> Action:
    """What the recorded evidence says to do next.

    `max_scan` bounds rule 1, which re-grades transcript exchanges against the
    matrix: that is the one rule whose cost grows with the run, and a ledger
    that takes a minute to answer is a ledger nobody consults. An audit
    measured a single call at over five minutes on a long run, with the cap
    at 400 and every line of every candidate response graded against the whole
    transcript. Rule 1 asks "do you already hold a proof you never recorded",
    which is a question about recent work, so the window is the honest bound
    rather than a reluctant one. Raise it to re-examine an old run.
    """
    sdir = Path(sdir)
    if not sdir.exists():
        return Action("open_session",
                      f"no session directory at {sdir}. A run records its "
                      "evidence before anything can be computed from it.")

    entries = _load_transcript(sdir)
    exchanges = _exchanges(entries)
    findings = _load_findings(sdir)

    if not exchanges:
        return Action("recon",
                      "the transcript holds no request/response pair yet. Map "
                      "the surface before classifying any of it: one "
                      "http_request against the target root, then the links "
                      "and forms it names.",
                      detail={"entries_recorded": len(entries)})

    index = _by_id(entries)
    claimed_ids = {str(i) for f in findings
                   for i in (f.get("evidence_ids") or [])}
    # Per (class, endpoint), not per class: an `rce` recorded on /a used to
    # hide an unrecorded `rce` proof on /b for the rest of the run, because
    # the class was "already recorded". Two endpoints are two findings.
    recorded = {(proof.normalize(str(f.get("vuln_class") or "")),
                 _endpoint(f) or _shape_of_url(str(f.get("url") or "")))
                for f in findings}

    # Rule 1 - evidence already on disk that meets a proof requirement, with
    # no finding recorded for it. This is the expensive-but-important case: the
    # probe worked and the run moved on without recording it.
    by_shape: dict[str, list[dict]] = {}
    for entry in exchanges:
        by_shape.setdefault(proof._endpoint_shape(entry), []).append(entry)
    unrecorded = _unrecorded_proof(exchanges, recorded, claimed_ids, max_scan,
                                   by_shape)
    if unrecorded is not None:
        klass, entry, verdict, cited = unrecorded
        # The ids handed over are the ones the grade was computed from. They
        # used to be `[entry.id]` alone while `grade_if_recorded` came from
        # a multi-exchange citation, so the promise was unreachable with the
        # evidence offered: every class whose requirement needs a pair or a
        # series grades lower on one entry than the number printed beside
        # it. An operator who cites exactly what the ledger hands them must
        # get exactly what the ledger promised.
        ids = [str(e.get("id")) for e in cited if e.get("id")]
        if str(entry.get("id")) not in ids:
            ids.insert(0, str(entry.get("id")))
        return Action(
            "record_finding",
            f"request {entry.get('id')} already meets the proof requirement "
            f"for {klass}, and no finding records it. Record it with the "
            f"{len(ids)} cited exchange(s) before probing anything else.",
            target=_endpoint(entry), vuln_class=klass,
            detail={"evidence_ids": ids,
                    "requirement": verdict.requirement,
                    "grade_if_recorded": verdict.grade})

    # Rule 2 - a recorded finding the matrix does not grade proven, where the
    # matrix names what is missing. The gap is the next probe.
    unreviewed: list[dict] = []
    for finding in findings:
        grade = str(finding.get("grade") or "")
        if grade == "proven" and not _reviewed(finding):
            unreviewed.append(finding)
        if grade in ("proven", "refused"):
            continue
        missing = [m for m in (finding.get("proof") or {}).get("missing", [])
                   if isinstance(m, str)]
        klass = proof.normalize(str(finding.get("vuln_class") or ""))
        if not missing:
            continue
        # A gap that probing cannot close starves every rule below this one
        # if it is recommended forever. `argus proof <class>` says why.
        #
        # There are TWO ways a class is in that state and this tested one.
        # The ceiling was the obvious one, and it is now empty - `xss` and
        # `ssrf` both came off when `argus/collector.py` gave their
        # payloads somewhere to call back to. The other is a class the
        # matrix REFUSES, and `dos` has always been one: no ceiling, so the
        # condition above never saw it, and the ledger would send an
        # operator to close a gap whose whole point is that it stays open.
        # The emptying is what exposed it; the defect predates it.
        spec = proof.spec_for(klass)
        if spec is not None and spec.ceiling and grade == spec.ceiling:
            continue
        if spec is not None and spec.verifier is proof.verify_refused:
            continue
        return Action(
            "close_proof_gap",
            f"{finding.get('id')} is {grade or 'ungraded'} for {klass}, not "
            f"proven. The matrix names exactly what is absent: "
            f"{'; '.join(missing[:3])}.",
            target=str(finding.get("url") or ""), vuln_class=klass,
            finding_id=str(finding.get("id") or ""),
            tool=_tool_for_class(klass),
            detail={"missing": missing,
                    "requirement": proof.requirement_of(klass),
                    "tool_chain": list(CLASS_TOOL_CHAIN.get(klass, ())),
                    "cited_evidence": finding.get("evidence_ids") or []})

    # Rule 3 - surface with named inputs that no class-bearing probe touched.
    counts = _probes_run(entries)
    surface = _surface(entries)
    untouched = [(ep, sorted(names)) for ep, names in sorted(surface.items())
                 if not any(k[0] == ep for k in counts)]
    if untouched:
        endpoint, names = untouched[0]
        return Action(
            "probe", f"{endpoint} carries {len(names)} named input(s) "
            f"({', '.join(names[:6])}) and no probe has tested any class "
            f"against it. Name one hypothesis and send a matched pair.",
            target=endpoint, tool=_FIRST_PASS[0],
            detail={"params": names,
                    "untested_endpoints": len(untouched),
                    "reading_order": list(_FIRST_PASS)})

    # Rule 4 - surface tested for some classes but not the first-pass set.
    gap = _class_gap(surface, counts)
    if gap is not None:
        endpoint, klass, tool = gap
        return Action(
            "probe", f"{endpoint} has been probed, but not for {klass}. "
            f"`argus proof {klass}` says what that class needs; collect it on "
            "the first pass.",
            target=endpoint, vuln_class=klass, tool=tool,
            detail={"params": sorted(surface.get(endpoint, ())),
                    "classes_tried": sorted(
                        k[1] for k in counts if k[0] == endpoint),
                    "requirement": proof.requirement_of(klass)})

    # Rule 5 - a class that has spent its budget on one endpoint with nothing
    # recorded. Park it by name and move, rather than sending payload six.
    spent = [(ep, klass, n) for (ep, klass), n in sorted(counts.items())
             if n >= BUDGET_PER_CLASS and (klass, ep) not in recorded]
    if spent:
        endpoint, klass, n = spent[0]
        return Action(
            "park_and_switch",
            # "about N probe calls" is gone, and so is
            # `probe_calls_allowed`. Both divided the recorded request count
            # by `REQUESTS_PER_PROBE`, which is 12 for every probe - and
            # measured against the lab one call records probe_reflection 1,
            # probe_cmdi 3, probe_redirect 3, probe_ssti 8, probe_lfi 8,
            # probe_sqli 11, probe_ssrf 11. So the figure was wrong by up to
            # 12x in either direction: at 61 recorded probe_reflection
            # requests, which on this lab is 61 calls, the ledger printed
            # "about 5 probe calls".
            #
            # The transcript carries no call-boundary field - an entry has
            # chain, id, request, response, tool, ts - so a call count is
            # not derivable from the evidence at all. `requests_sent` and
            # `budget_requests` both are, and they are what the operator
            # needs to see. `BUDGET_PER_CLASS` stays as a budget, which is a
            # policy constant and not a measurement.
            f"{klass} on {endpoint} has taken {n} of its "
            f"{BUDGET_PER_CLASS}-request budget and recorded no finding. "
            "Say in notes.md what was ruled out and what would revive it, "
            "then open a different class.",
            target=endpoint, vuln_class=klass,
            detail={"requests_sent": n, "budget_requests": BUDGET_PER_CLASS,
                    "classes_untried": _untried(surface, counts, endpoint)})

    # Rule 6 - findings exist and are proven, but nothing has widened the
    # surface. A single proven class is not an engagement.
    if findings and len(surface) <= 1:
        return Action(
            "widen_surface",
            f"{len(findings)} finding(s) on {len(surface)} endpoint(s). "
            "Another host, another port, a second credential tier, or an "
            "input kind the first pass skipped - headers, cookies, path "
            "segments, uploaded file names.",
            detail={"endpoints_known": sorted(surface),
                    "findings": [f.get("id") for f in findings]})

    # Rule 6b - nothing was probed at all. Rule 7 is the only exit and it
    # used to be reachable from a single fetch of a root page with no
    # parameters anywhere: no surface, so rules 3-5 pass, no findings, so
    # rule 6 passes, and the ledger said "write the report" about a run that
    # had tested nothing.
    if not counts:
        return Action(
            "recon",
            "nothing on record has been probed for any class, and no "
            "parameterised endpoint was reached. Map more surface before "
            "concluding anything: follow the links and forms this response "
            "names, and look at headers, cookies and path segments as inputs "
            "too.",
            detail={"exchanges": len(exchanges),
                    "endpoints_seen": sorted(
                        {_endpoint(e) for e in exchanges if _endpoint(e)})[:20],
                    "parameterised": sorted(surface)})

    # Rule 6b - PROVEN BY THE MATRIX, READ BY NOBODY ELSE.
    #
    # The matrix proves a claim's BYTES: "the target produced the quoted
    # bytes" is a universal check and a fabricated excerpt fails it, so an
    # invented command output cannot reach `proven`. Measured: an `id`
    # output that no recorded response contains grades `unproven` and names
    # three failing checks.
    #
    # What the matrix does not read is the INTERPRETATION. Bytes that really
    # came off the wire can still be the wrong class, or a lower severity
    # than claimed, or a reflection presented as execution. `argus judge`
    # exists for exactly that - a model from a different family reads the
    # cited evidence records and never the first model's reasoning - and
    # nothing ever asked for it. Rule 2 above skips a `proven` finding as
    # finished, so an engagement could seal with every finding's bytes
    # verified and no finding's reading checked by anyone.
    #
    # Placed immediately before the only exit, and not earlier. Breadth is
    # still the engagement's job, so `widen_surface` and the class-gap rules
    # keep their priority; what changes is that the exit is no longer
    # reachable while a finding this run will REPORT has been read by one
    # model only. Rule 7's own sentence names the distinction it was missing:
    # it said every finding is "graded", and graded is not reviewed.
    if unreviewed:
        finding = unreviewed[0]
        fid = str(finding.get("id") or "")
        klass = proof.normalize(str(finding.get("vuln_class") or ""))
        return Action(
            "cross_verify",
            f"{fid} is proven: the target produced the bytes it quotes. No "
            f"second model has read those bytes, so its reading as {klass} "
            f"is the first model's alone. `argus judge <session>` picks a "
            f"judge from another family; it cannot change the grade, only "
            f"dispute the class, the severity or the conclusion.",
            vuln_class=klass, finding_id=fid,
            detail={"unreviewed": [str(f.get("id") or "") for f in unreviewed],
                    "reviewed_by": [], "grade": "proven"})

    # Rule 7 - the only exit.
    return Action(
        "report",
        "every parameterised endpoint in the transcript has been probed for "
        "the first-pass classes, every recorded finding is graded, and every "
        "proven one has been read by a model from another family. Write "
        "the report: proven findings with their proofs, candidates with the "
        "exact missing check, and what was ruled out.",
        detail={"endpoints": len(surface), "findings": len(findings),
                "grades": sorted({str(f.get("grade")) for f in findings}),
                "probe_requests": sum(counts.values())})


def _unrecorded_proof(exchanges: list[dict], recorded: set[str],
                      claimed_ids: set[str], max_scan: int,
                      by_shape: dict | None = None):
    """An exchange that would grade proven for a class nothing recorded.

    Deliberately narrow. It only considers exchanges a class-bearing probe
    produced, and only for that probe's own class: re-grading every exchange
    against all 29 classes would turn any page that echoes its query into a
    recommendation to record sqli, which is the exact failure the proof matrix
    exists to prevent.
    """
    by_shape = by_shape if by_shape is not None else {}
    for entry in reversed(exchanges[-max_scan:]):
        klass = PROBE_CLASS.get(_tool_of(entry))
        if not klass or (klass, _endpoint(entry)) in recorded:
            continue
        if str(entry.get("id")) in claimed_ids:
            continue
        # Cite the entry plus its NEIGHBOURS on the same endpoint, which is
        # where a control lives. Two bounds matter and they pull against
        # each other: a single-entry claim can only ever pass the classes
        # that need no pair, while citing the whole transcript makes every
        # grade quadratic in the run - an audit measured one call at over
        # five minutes. The local window is the honest middle: it is what a
        # tester would cite, and it is O(1) per candidate.
        cited = _neighbours(entry, by_shape)
        group = by_shape.get(proof._endpoint_shape(entry)) or [entry]
        for excerpt in _excerpts(proof.resp_body(entry)):
            verdict = proof.grade(klass, excerpt, cited)
            if not verdict.proven:
                continue
            # The window is a FILTER, not the evidence. For a requirement
            # that is a negative universal - lockout's is "a counted series
            # of at least five FAILED attempts ... NONE of them refused" -
            # removing exchanges is strictly favourable, so a window can
            # only ever grade the same or higher than the full record. The
            # window was introduced to bound cost (the whole-transcript
            # version was measured at over five minutes) and nothing
            # re-checked the classes whose requirement is a count.
            #
            # Measured against the live lab's `/login3`, which locks after
            # five attempts: r1-r5 answered 200 "Invalid credentials." and
            # r6 answered 429 "Account locked - too many attempts". The
            # window around r2 is r1..r5 and omits r6. The SAME excerpt
            # graded `proven` against the window and `candidate` against
            # all six, missing `['none of them was refused']` - so the
            # ledger, which is sold as the reader that cannot be talked
            # round because it never saw the conversation, told the
            # operator to record "this target has no lockout" about a
            # target that had just locked the account.
            #
            # So: confirm against everything recorded on this endpoint
            # before recommending. The cost argument survives because this
            # runs at most once per call - only a candidate that already
            # passed the cheap window gets here - while the whole-transcript
            # version graded every candidate that way.
            confirmed = proof.grade(klass, excerpt, group)
            if not confirmed.proven:
                continue
            return klass, entry, confirmed, group
    return None


def _neighbours(entry: dict, by_shape: dict) -> list[dict]:
    """The candidate plus the nearest exchanges on the same endpoint."""
    group = by_shape.get(proof._endpoint_shape(entry)) or [entry]
    try:
        at = group.index(entry)
    except ValueError:
        return [entry]
    lo = max(0, at - _NEIGHBOURS)
    window = group[lo:at + _NEIGHBOURS + 1]
    return window if entry in window else [entry, *window[:_NEIGHBOURS]]


# Exchanges on either side of a candidate that rule 1 cites with it. Rule 1
# is the only rule whose work grows with the run, and it is the one an audit
# measured at over five minutes: each grade runs `_pairs` over the cited set,
# which is quadratic. A local window keeps it O(1) per candidate and is also
# what a tester would cite - the control for a probe is the request next to
# it, not something four hundred requests away.
_NEIGHBOURS = 3


def _excerpts(body: str, limit: int = 8) -> list[str]:
    """Candidate quotes from a response, as a tester would cut them.

    Handing the whole body to the matrix defeats its own echo veto: a body
    always contains some byte the request did not, so "the target produced
    the quoted bytes" passes for free and a page that merely reflected the
    payload looks like a proof. A real finding quotes a line. So does this.
    """
    if not body:
        return []
    out, seen = [], set()
    for line in body.splitlines():
        line = line.strip()
        if not (8 <= len(line) <= 400) or line in seen:
            continue
        seen.add(line)
        out.append(line)
        if len(out) >= limit:
            break
    # a short single-line body is itself the quote a tester would take
    whole = body.strip()
    if whole and len(whole) <= 400 and whole not in seen:
        out.append(whole)
    return out


def _tool_for_class(klass: str) -> str:
    chain = CLASS_TOOL_CHAIN.get(klass)
    if chain:
        return chain[0]
    for tool, mapped in PROBE_CLASS.items():
        if mapped == klass:
            return tool
    return "http_request"


def _class_gap(surface: dict[str, set[str]],
               counts: dict[tuple[str, str], int]):
    for endpoint in sorted(surface):
        tried = {k[1] for k in counts if k[0] == endpoint}
        for tool in _FIRST_PASS:
            klass = PROBE_CLASS[tool]
            if klass not in tried:
                return endpoint, klass, tool
    return None


def _untried(surface: dict[str, set[str]],
             counts: dict[tuple[str, str], int], endpoint: str) -> list[str]:
    tried = {k[1] for k in counts if k[0] == endpoint}
    return [PROBE_CLASS[t] for t in _FIRST_PASS if PROBE_CLASS[t] not in tried]
