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
    "probe_lfi": "lfi", "probe_idor": "idor", "probe_redirect": "redirect",
    "probe_xxe": "xxe", "probe_deserialize": "deserialize",
    "probe_cors": "cors", "probe_csrf": "csrf", "probe_cache": "cache",
    "probe_xfh": "xfh", "probe_massassign": "massassign",
    "probe_lockout": "lockout", "probe_enum": "enum",
    "probe_upload": "upload", "probe_crlf": "crlf",
    "probe_method": "method", "probe_race": "race",
    "probe_smuggle": "smuggle", "probe_ppoll": "ppoll",
    "probe_websocket": "websocket", "probe_disclosure": "disclosure",
}
# `probe_time` is deliberately absent: a latency measurement is consistent
# with sqli, with rce, and with a slow database, so recording it as "this
# class was tested" would let a timing run stand in for a proof it cannot
# produce. The same reasoning excludes the recon tools - mapping
# `fingerprint` to a class would make reading a banner count as probing.

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
REQUESTS_PER_PROBE = 12
PROBE_CALLS_PER_CLASS = 5
BUDGET_PER_CLASS = REQUESTS_PER_PROBE * PROBE_CALLS_PER_CLASS

_STATIC_RE = re.compile(
    r"\.(?:css|js|mjs|map|png|jpe?g|gif|svg|ico|woff2?|ttf|eot|webp|avif|"
    r"mp4|webm|pdf|zip|gz)(?:$|\?)", re.I)


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
    return [f for f in (data or []) if isinstance(f, dict)]


def _exchanges(entries: list[dict]) -> list[dict]:
    return [e for e in entries if isinstance(e.get("response"), dict)]


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
    recorded = {proof.normalize(str(f.get("vuln_class") or ""))
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
        klass, entry, verdict = unrecorded
        return Action(
            "record_finding",
            f"request {entry.get('id')} already meets the proof requirement "
            f"for {klass}, and no finding records it. Record it with that "
            f"exchange cited before probing anything else.",
            target=_endpoint(entry), vuln_class=klass,
            detail={"evidence_ids": [entry.get("id")],
                    "requirement": verdict.requirement,
                    "grade_if_recorded": verdict.grade})

    # Rule 2 - a recorded finding the matrix does not grade proven, where the
    # matrix names what is missing. The gap is the next probe.
    for finding in findings:
        grade = str(finding.get("grade") or "")
        if grade in ("proven", "refused"):
            continue
        missing = [m for m in (finding.get("proof") or {}).get("missing", [])
                   if isinstance(m, str)]
        klass = proof.normalize(str(finding.get("vuln_class") or ""))
        if not missing:
            continue
        # A class capped at `candidate` cannot be closed by more probing, so
        # recommending it forever starves every rule below this one. `argus
        # proof <class>` says why the cap is there; the ledger should move on.
        spec = proof.spec_for(klass)
        if spec is not None and spec.ceiling and grade == spec.ceiling:
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
             if n >= BUDGET_PER_CLASS and klass not in recorded]
    if spent:
        endpoint, klass, n = spent[0]
        return Action(
            "park_and_switch",
            f"{klass} on {endpoint} has taken {n} requests - about "
            f"{n // REQUESTS_PER_PROBE} probe calls - and recorded no "
            "finding. Say in notes.md what was ruled out and what would "
            "revive it, then open a different class.",
            target=endpoint, vuln_class=klass,
            detail={"requests_sent": n, "budget_requests": BUDGET_PER_CLASS,
                    "probe_calls_allowed": PROBE_CALLS_PER_CLASS,
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

    # Rule 7 - the only exit.
    return Action(
        "report",
        "every parameterised endpoint in the transcript has been probed for "
        "the first-pass classes, and every recorded finding is graded. Write "
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
        if not klass or klass in recorded:
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
        for excerpt in _excerpts(proof.resp_body(entry)):
            verdict = proof.grade(klass, excerpt, cited)
            if verdict.proven:
                return klass, entry, verdict
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
