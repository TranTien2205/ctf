"""Cross-family verification: a second model reads the evidence, not the claim.

Ported from the orchestrator plane, with one rule added that the original did
not need and this tree does:

    **a judge can lower a grade or dispute a finding. It can never raise one.**

The proof matrix is deterministic and auditable; a model's opinion is neither.
Letting an opinion promote a `candidate` to `proven` would put the strongest
claim this system makes behind the weakest check it has. So `proven` here means
exactly what `argus/proof.py` said it means, and the judge's output is a
separate field a reader can weigh.

What a judge is for, then, is the gap the matrix cannot see. The matrix grades
whether the cited bytes meet a class's requirement. It does not know whether
the finding is filed under the right class, whether the title claims more than
the bytes support, or whether the severity is defensible. Those are judgements,
and a model from a different family is a real second opinion on them - two
models that agree because they share a prior are not a check.

What the judge is shown: the finding, its class's proof requirement, and the
cited evidence records. Never the first model's reasoning, because the
disagreement worth having is the one that reasoning would not produce.

**This case file leaves the machine.** It goes to a different vendor than the
one that ran the engagement, so `render_case` re-redacts everything it
assembles rather than trusting that the recorder already did. Transcript
entries are redacted on the way in - but "already redacted" is a property of
the write path, and a function that ships bytes to a third party should not
rest on a promise made somewhere else. `argus report` re-redacts old
transcripts at render for exactly this reason. Before this, a target's
`Set-Cookie`, an `api_key=` in a body, a JWT and a URL's userinfo all reached
the other vendor verbatim.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from . import models as models_mod
from . import proof
from .httpclient import _redact_headers
from .session import _redact_url

# Credential shapes that must not leave the machine even if no recorder rule
# caught them: a key pasted into a BODY is not a header, and no header rule
# redacts it.
_REDACTED = "\u2022\u2022\u2022redacted\u2022\u2022\u2022"
_SCRUB = (
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]{16,}"),
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwd|pwd)"
               r"(\s*[=:]\s*)[\'\"]?[^\s\'\",;&]{8,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+"),
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{16,}"
               r"|AKIA[0-9A-Z]{12,})"),
)


# `scheme://user:pass@host` ANYWHERE in prose. `_redact_url` only works
# when the whole string is a URL, so calling it on a case-file blob was a
# no-op - a line that looked like a defence and could not fire. Measured:
# `"target is http://admin:SuperSecret123@10.0.0.5/app now"` came back
# unchanged. This text goes to a SECOND vendor, which is the strongest
# reason to scrub it rather than the weakest.
#
# Only the password is replaced, so the host and the username still read -
# a judge asked whether a disclosure happened needs to see the shape of
# what leaked, not its value.
_URL_USERINFO = re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://[^\s/@:]+:)"
                           r"[^\s/@]+(@)")


def _scrub(text: str) -> str:
    """Re-redact credential shapes before the text leaves the machine."""
    out = _URL_USERINFO.sub(lambda m: m.group(1) + _REDACTED + m.group(2),
                            _redact_url(str(text or "")))
    for pattern in _SCRUB:
        out = pattern.sub(
            lambda m: "".join(g for g in m.groups() if g) + _REDACTED
            if m.groups() and any(m.groups()) else _REDACTED, out)
    return out

PROMPT = """\
You are reviewing another model's finding from an authorised penetration test.
You are from a different model family on purpose: the useful disagreement is
the one the first model's own reasoning would not have produced.

You are shown the finding, the proof requirement for its class, and the raw
evidence records. You are NOT shown the first model's reasoning, and you
should not try to reconstruct it.

Answer this and nothing else: **does the evidence, on its own, establish the
claim the finding makes?**

Dispute it if any of these is true:
- the observation could have happened with the vulnerability absent
- a control is missing, so an asymmetry has no baseline
- the requirement's checks are met only in appearance: a nonce that was never
  sent, a table with no rows, a reflected payload treated as execution, a
  scanner label treated as evidence
- the claim is broader than the evidence: one readable record reported as
  "every record", one endpoint reported as "the application"
- the finding is filed under the wrong class for what the bytes actually show
- the severity is not defensible from the evidence

You cannot promote a finding. If the evidence is stronger than the grade says,
say so in `reason` - the grade is decided by a deterministic matrix, not here.

Return exactly one JSON object and nothing else:

{"agrees": true|false,
 "reason": "<one or two sentences, pointing at the specific record or the \
missing control>",
 "severity": "critical|high|medium|low|info",
 "class": "<the class the evidence actually shows, or the same one>",
 "missing": ["<what would settle it, if anything>"]}"""

_SEVERITIES = ("critical", "high", "medium", "low", "info")
_TRUE = {"true", "yes", "1"}
_FALSE = {"false", "no", "0"}


def _as_bool(value) -> bool | None:
    """A real boolean, or the words for one. Anything else is no answer.

    `bool("false")` is True, which is how a judge that disagreed was recorded
    as agreeing.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return bool(value)
    if isinstance(value, str):
        word = value.strip().lower()
        if word in _TRUE:
            return True
        if word in _FALSE:
            return False
    return None
_RANK = {s: n for n, s in enumerate(_SEVERITIES)}


@dataclass
class Verdict:
    """One judge's reading of one finding."""
    finding_id: str
    judge_model: str
    agrees: bool
    reason: str = ""
    severity: str = ""
    vuln_class: str = ""
    missing: list[str] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict:
        out = {"finding_id": self.finding_id, "judge_model": self.judge_model,
               "agrees": self.agrees}
        for key in ("reason", "severity", "vuln_class", "error"):
            if getattr(self, key):
                out[key] = getattr(self, key)
        if self.missing:
            out["missing"] = self.missing
        return out


def pick_judge(author_model: str, policy: str = "strong"):
    """A judge from a family the author does not belong to, or nothing.

    Returning nothing is a real answer: with only one family credentialed
    there is no independent judge to be had, and running the author's own
    family as its own reviewer while calling it cross-verification would be
    the kind of claim this system exists not to make.
    """
    family = models_mod.family(author_model)
    if family == "unknown":
        # We cannot exclude a family we cannot name, so "cross-family" would
        # be a claim with nothing behind it. Refusing is the honest answer:
        # the operator can name a judge explicitly if they know better.
        return None
    pick = models_mod.for_role("judge", policy, exclude_family=family)
    if pick is None:
        return None
    if pick.provider != "anthropic" and not pick.credential():
        return None
    return pick


def _kind_of(entry: dict) -> str:
    """What this record IS, for a judge reading the case file.

    Every cited record was labelled `(event)` - the word this module's own
    prompt uses for evidence that is not class evidence - so a judge reading
    a real request/response pair was told it was not one.
    """
    if isinstance(entry.get("response"), dict):
        return "http exchange"
    return str(entry.get("kind") or "event")


def render_case(finding: dict, entries: list[dict]) -> str:
    """The case file a judge reads: claim, requirement, cited bytes."""
    klass = proof.normalize(str(finding.get("vuln_class") or ""))
    requirement = proof.requirement_of(klass) or "(no requirement on file)"
    verdict = finding.get("proof") if isinstance(
        finding.get("proof"), dict) else {}
    lines = [
        "## The finding",
        f"- id: {finding.get('id')}",
        f"- title: {finding.get('title')}",
        f"- class: {klass}",
        f"- severity claimed: {finding.get('severity')}",
        f"- url: {_scrub(str(finding.get('url') or ''))}",
        f"- grade from the proof matrix: {finding.get('grade')}",
    ]
    if verdict.get("missing"):
        lines.append(f"- checks the matrix found absent: "
                     f"{', '.join(str(m) for m in verdict['missing'][:6])}")
    lines += [
        "",
        f"## The proof requirement for {klass}",
        requirement,
        "",
        "## The quoted evidence",
        "```",
        _scrub(str(finding.get("evidence_excerpt") or ""))[:4000],
        "```",
        "",
        "## The cited records",
    ]
    if not entries:
        lines.append("(none - the finding cites no recorded exchange)")
    for entry in entries[:6]:
        req = entry.get("request") if isinstance(
            entry.get("request"), dict) else {}
        resp = entry.get("response") if isinstance(
            entry.get("response"), dict) else {}
        req_headers = req.get("headers") if isinstance(
            req.get("headers"), dict) else {}
        lines += [
            "",
            f"### {entry.get('id')} ({_kind_of(entry)})",
            _scrub(f"{req.get('method', '')} {req.get('url', '')}".strip())
            or "(no request recorded)",
        ]
        if req_headers:
            shown = _redact_headers(
                {str(k): str(v) for k, v in list(req_headers.items())[:12]},
                set())
            lines.append(
                f"request headers: {json.dumps(shown, default=str)[:600]}")
        body = req.get("body")
        if body:
            lines += ["request body:", "```", _scrub(str(body))[:1200], "```"]
        if resp:
            lines.append(f"-> HTTP {resp.get('status')}")
            headers = resp.get("headers") if isinstance(
                resp.get("headers"), dict) else {}
            if headers:
                shown = _redact_headers(
                    {str(k): str(v) for k, v in list(headers.items())[:12]},
                    set())
                lines.append(f"headers: {json.dumps(shown, default=str)[:600]}")
            lines += ["body:", "```",
                      _scrub(str(resp.get("body") or ""))[:3000], "```"]
        else:
            lines.append(_scrub(json.dumps(
                {k: v for k, v in entry.items()
                 if k not in ("chain", "id", "ts")}, default=str))[:1200])
    return "\n".join(lines)


def parse_verdict(text: str, finding_id: str, judge_model: str) -> Verdict:
    """Read one JSON object out of a model's answer.

    A judge that answers in prose is a judge that did not answer, and
    guessing at its intent would manufacture agreement. An unparseable reply
    is recorded as no verdict, not as assent.
    """
    raw = str(text or "")
    # One pass, not one per brace. The old scan restarted from every `{` and
    # ran to the end of the reply, so an 8 KB answer with nested objects took
    # seconds - per finding. Depth tracking finds the same balanced objects in
    # a single sweep, and skips braces inside strings, which the old scan
    # counted.
    found: list[dict] = []
    depth, start, in_string, escaped = 0, -1, False, False
    for i, ch in enumerate(raw):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth:
                depth -= 1
                if depth == 0 and start != -1:
                    try:
                        candidate = json.loads(raw[start:i + 1])
                    except ValueError:
                        candidate = None
                    if isinstance(candidate, dict) and "agrees" in candidate:
                        found.append(candidate)
                    start = -1
    if not found:
        return Verdict(finding_id, judge_model, agrees=False,
                       error="the judge returned no JSON object carrying "
                             "`agrees`; recorded as no verdict, not as assent",
                       reason=raw.strip()[:300])
    if len({bool(d.get("agrees")) for d in found}) > 1:
        # A model that illustrated the format and then answered, and a model
        # that answered and then hedged, produce the same two objects in the
        # same order. Picking one would be a guess, and a guess that lands on
        # "agrees" manufactures the assent this whole module exists to avoid.
        return Verdict(finding_id, judge_model, agrees=False,
                       error=f"the judge returned {len(found)} verdicts that "
                             "contradict each other; recorded as no verdict",
                       reason=raw.strip()[:300])
    # They agree on the answer. The LAST one is not necessarily the fullest:
    # a model that answers and then appends `Summary: {"agrees": false}` put
    # its reason, severity and missing list in the first object, and taking
    # the last discarded all three. Merge instead - later objects win on the
    # fields they actually carry, earlier detail survives where they do not.
    data = {}
    for obj in found:
        data.update({k: v for k, v in obj.items()
                     if v not in (None, "", [], {})})
    data["agrees"] = found[-1].get("agrees")
    severity = str(data.get("severity") or "").strip().lower()
    # A scalar `missing` was iterated into characters, so a judge answering
    # `"missing": "a control"` produced ['a', ' ', 'c', 'o', ...] in the
    # report. A string is one item, not eight.
    raw_missing = data.get("missing")
    if isinstance(raw_missing, (str, int, float)):
        raw_missing = [raw_missing]
    elif not isinstance(raw_missing, (list, tuple)):
        raw_missing = []
    missing = [str(m)[:300] for m in raw_missing
               if isinstance(m, (str, int, float))][:8]
    # `bool()` on the reply made a judge answering `"agrees": "false"` read as
    # AGREEING - any non-empty string is truthy. Of all the ways to be wrong
    # here that is the worst one, because it manufactures the assent this
    # whole module exists to avoid. Only a real boolean, or the words, count.
    agrees = _as_bool(data.get("agrees"))
    if agrees is None:
        return Verdict(finding_id, judge_model, agrees=False,
                       error=f"the judge's `agrees` was "
                             f"{data.get('agrees')!r}, which is neither true "
                             "nor false; recorded as no verdict",
                       reason=str(data.get("reason") or "")[:300])
    return Verdict(
        finding_id, judge_model,
        agrees=agrees,
        reason=str(data.get("reason") or "")[:1000],
        severity=severity if severity in _SEVERITIES else "",
        vuln_class=proof.normalize(str(data.get("class") or "")),
        missing=missing)


def apply_verdict(finding: dict, verdict: Verdict) -> dict:
    """Fold a verdict into a finding WITHOUT ever raising its standing.

    Three one-way doors: a dispute records `disputed` and never clears it, a
    severity can only move down, and `grade` is not touched at all - that
    field belongs to the proof matrix.
    """
    out = dict(finding)
    # Every verdict is KEPT, not overwritten. A second judge that agrees used
    # to replace the first one's block, so a report read "Cross-verification:
    # agreed" over a finding whose `disputed` flag was still set - telling the
    # reader the opposite of the record. A dispute is a one-way door; later
    # agreement is additional information, not a correction.
    history = finding.get("judges")
    history = list(history) if isinstance(history, list) else (
        [finding["judge"]] if isinstance(finding.get("judge"), dict) else [])
    history.append(verdict.to_dict())
    out["judges"] = history
    out["judge"] = verdict.to_dict()
    # A transport failure or an unparseable reply is NO VERDICT, which this
    # module's own docstring says is not a dispute - and `apply_verdict`
    # marked it disputed anyway, because it only looked at `agrees`. A judge
    # that could not be reached has not disagreed with anything.
    if not verdict.agrees and not verdict.error:
        out["disputed"] = True
    if verdict.severity:
        raw = str(out.get("severity") or "").lower()
        proposed = _RANK.get(verdict.severity, 99)
        if raw not in _RANK:
            # No canonical severity to compare against - an unrated or
            # misspelled finding used to swallow the reduction silently,
            # which is the one direction this module is supposed to allow.
            out["severity_claimed"] = out.get("severity")
            out["severity"] = verdict.severity
            out["severity_was_unrated"] = True
        elif proposed > _RANK[raw]:     # higher rank number = less severe
            out["severity_claimed"] = out.get("severity")
            out["severity"] = verdict.severity
    if (verdict.vuln_class
            and verdict.vuln_class != proof.normalize(
                str(out.get("vuln_class") or ""))):
        out["class_disputed"] = verdict.vuln_class
    return out


def judge_finding(llm, finding: dict, entries: list[dict],
                  judge_model: str) -> Verdict:
    """One call. A transport failure is a missing verdict, not a dispute."""
    case = render_case(finding, entries)
    try:
        reply = llm.chat(
            messages=[{"role": "user", "content": case}],
            tools=[], system=PROMPT)
    except Exception as exc:
        return Verdict(str(finding.get("id") or ""), judge_model, agrees=False,
                       error=f"{type(exc).__name__}: {exc}")
    text = ""
    for block in (reply or {}).get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            text += str(block.get("text") or "")
    return parse_verdict(text, str(finding.get("id") or ""), judge_model)
