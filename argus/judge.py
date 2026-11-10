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
cited evidence records, redacted. Never the first model's reasoning, because
the disagreement worth having is the one that reasoning would not produce.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from . import models as models_mod
from . import proof

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
    pick = models_mod.for_role("judge", policy, exclude_family=family)
    if pick is None:
        return None
    if pick.provider != "anthropic" and not pick.credential():
        return None
    return pick


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
        f"- url: {finding.get('url')}",
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
        str(finding.get("evidence_excerpt") or "")[:4000],
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
        lines += [
            "",
            f"### {entry.get('id')} ({entry.get('kind', 'event')})",
            f"{req.get('method', '')} {req.get('url', '')}".strip()
            or "(no request recorded)",
        ]
        body = req.get("body")
        if body:
            lines += ["request body:", "```", str(body)[:1200], "```"]
        if resp:
            lines.append(f"-> HTTP {resp.get('status')}")
            headers = resp.get("headers") if isinstance(
                resp.get("headers"), dict) else {}
            if headers:
                shown = {k: v for k, v in list(headers.items())[:12]}
                lines.append(f"headers: {json.dumps(shown, default=str)[:600]}")
            lines += ["body:", "```", str(resp.get("body") or "")[:3000], "```"]
        else:
            lines.append(json.dumps(
                {k: v for k, v in entry.items()
                 if k not in ("chain", "id", "ts")}, default=str)[:1200])
    return "\n".join(lines)


def parse_verdict(text: str, finding_id: str, judge_model: str) -> Verdict:
    """Read one JSON object out of a model's answer.

    A judge that answers in prose is a judge that did not answer, and
    guessing at its intent would manufacture agreement. An unparseable reply
    is recorded as no verdict, not as assent.
    """
    raw = str(text or "")
    found: list[dict] = []
    start = raw.find("{")
    while start != -1:
        depth, end = 0, -1
        for i in range(start, len(raw)):
            if raw[i] == "{":
                depth += 1
            elif raw[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end == -1:
            break
        try:
            candidate = json.loads(raw[start:end])
        except ValueError:
            candidate = None
        if isinstance(candidate, dict) and "agrees" in candidate:
            found.append(candidate)
        start = raw.find("{", start + 1)
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
    # they agree on the answer, so the last one carries the fullest detail
    data = found[-1]
    severity = str(data.get("severity") or "").strip().lower()
    missing = [str(m)[:300] for m in (data.get("missing") or [])
               if isinstance(m, (str, int, float))][:8]
    return Verdict(
        finding_id, judge_model,
        agrees=bool(data.get("agrees")),
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
    out["judge"] = verdict.to_dict()
    if not verdict.agrees:
        out["disputed"] = True
    if verdict.severity:
        current = _RANK.get(str(out.get("severity") or "").lower(), 99)
        proposed = _RANK.get(verdict.severity, 99)
        if proposed > current:          # higher rank number = less severe
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
