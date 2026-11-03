"""ledger — the ledger itself, as tools.

A model that can read the ledger and must write through it behaves differently
from one that keeps its state in a context window. It can be interrupted,
handed to a different model, or resumed tomorrow, and the engagement is still
exactly where it was: the open hypotheses, the spent budgets, the evidence and
the parked branches are on disk rather than in a conversation.

`ledger.next_action` is the one to call when unsure what to do. It is computed
from recorded evidence, so it does not drift with the conversation.
"""
from __future__ import annotations

import json

from ... import config
from ...ledger import decide as decide_mod
from ...ledger import hooks
from ...ledger import report as report_mod
from ...ledger.state import State
from ..mcp import Server, ToolContext

SERVER = Server("ledger", "engagement state, hypotheses, evidence, findings, report")


def _outcome(outcome: hooks.Outcome, extra_next: str = "") -> dict:
    return {
        "ok": outcome.ok,
        "error": outcome.refusal,
        "summary": outcome.message,
        "data": outcome.data,
        "next": extra_next or ("" if outcome.ok else
                               "this is a refusal from the ledger, not a transport failure: "
                               "change the request, not the retry count"),
    }


@SERVER.tool(
    "ledger.status",
    "The compact state of the engagement: targets, surface counts, open hypotheses with their "
    "priorities, probes by class, findings with their proof grades, budgets and which escalation "
    "strategies are still unspent. Read this first in any session.",
    {"properties": {}, "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def status(context: ToolContext) -> dict:
    digest = context.state.digest()
    return {"summary": (f"{len(digest['targets'])} target(s), "
                        f"{len(digest['hypotheses']['open'])} open hypothesis(es), "
                        f"{len(digest['findings'])} finding(s), "
                        f"{digest['probes']['total']} probe(s)"),
            "data": digest,
            "output": json.dumps(digest, ensure_ascii=False, indent=2)[:8000]}


@SERVER.tool(
    "ledger.next_action",
    "What the controller says happens next, computed from recorded evidence rather than from the "
    "conversation. It returns the action, the reason, and the cheapest unrun ladder step. You may "
    "depart from it — say why, in the note on whatever you do instead.",
    {"properties": {}, "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def next_action(context: ToolContext) -> dict:
    action = decide_mod.decide(context.engagement)
    return {"summary": f"{action.action}: {action.why}", "data": action.to_dict(),
            "output": action.render()}


@SERVER.tool(
    "ledger.add_target",
    "Admit a target to the engagement. Refused unless it matches the scope, which is the point.",
    {"properties": {"target": {"type": "string"}, "note": {"type": "string"}},
     "required": ["target"]}, tier=config.TIER_PASSIVE, touches_target=False,
)
def add_target(context: ToolContext, target: str, note: str = "") -> dict:
    return _outcome(hooks.add_target(context.engagement, target, note))


@SERVER.tool(
    "ledger.add_surface",
    "Record an input or an endpoint found outside the broker's own tools — from a browser session, "
    "a proxy, a document, a source read. Surface is where classes live, so it belongs in the "
    "ledger however it was found.",
    {"properties": {"target": {"type": "string"},
                    "kind": {"type": "string",
                             "enum": ["port", "endpoint", "param", "form", "header", "cookie",
                                      "candidate", "credential", "file"]},
                    "value": {"type": "string"},
                    "detail": {"type": "object"}},
     "required": ["target", "kind", "value"]}, tier=config.TIER_PASSIVE, touches_target=False,
)
def add_surface(context: ToolContext, target: str, kind: str, value: str,
                detail: dict | None = None) -> dict:
    state = context.state
    verdict = state.scope.check(target)
    if not verdict:
        return {"ok": False, "error": "out-of-scope", "summary": verdict.reason}
    item = state.add_surface(target, kind, value, source="manual", detail=detail)
    state.save()
    return {"summary": f"surface {item['id']}: {kind} {value} on {target}", "data": item}


@SERVER.tool(
    "ledger.open_hypothesis",
    "Open a falsifiable hypothesis: one class, one entry point, one statement, and the observation "
    "that would kill it. Nothing may be probed without one — a probe that names no hypothesis "
    "cannot falsify anything, and a session of such probes produces confident prose instead of a "
    "finding.",
    {"properties": {
        "target": {"type": "string"},
        "vuln_class": {"type": "string", "description": "a class from the proof matrix"},
        "statement": {"type": "string", "description": "what is believed, specifically"},
        "falsifier": {"type": "string", "description": "the observation that would close it"},
        "entry_point": {"type": "object", "description": "e.g. {\"param\": \"id\", \"location\": \"query\"}"},
        "priority": {"type": "integer", "description": "0-100, default 50"},
    }, "required": ["target", "vuln_class", "statement"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def open_hypothesis(context: ToolContext, target: str, vuln_class: str, statement: str,
                    falsifier: str = "", entry_point: dict | None = None,
                    priority: int = 50) -> dict:
    from ...ledger import proof as matrix
    state = context.state
    verdict = state.scope.check(target)
    if not verdict:
        return {"ok": False, "error": "out-of-scope", "summary": verdict.reason}
    spec = matrix.spec_for(vuln_class)
    if spec is None:
        return {"ok": False, "error": "unknown-class",
                "summary": f"{vuln_class!r} has no proof requirement. Known: {matrix.classes()}",
                "next": "pick the class the evidence would belong to, or add a spec to the matrix"}
    if spec.verifier is matrix.verify_refused:
        return {"ok": False, "error": "refused-class", "summary": spec.refusal}
    item = state.add_hypothesis(target, spec.vuln_class, statement, entry_point, priority, falsifier)
    state.save()
    state.event("hypothesis.opened", {"hypothesis": item["id"], "class": spec.vuln_class})
    return {"summary": f"{item['id']} open: {spec.vuln_class} on {target}",
            "data": {"hypothesis": item, "requirement": spec.requirement,
                     "required_checks": list(spec.required_checks)},
            "next": f"to prove it you will need: {spec.requirement}"}


@SERVER.tool(
    "ledger.park",
    "Park a hypothesis at priority 0. Park, do not delete: a direction that looks wrong is usually "
    "unfinished, and a parked branch comes back the moment new evidence arrives.",
    {"properties": {"hypothesis_id": {"type": "string"}, "reason": {"type": "string"}},
     "required": ["hypothesis_id", "reason"]}, tier=config.TIER_PASSIVE, touches_target=False,
)
def park(context: ToolContext, hypothesis_id: str, reason: str) -> dict:
    return _outcome(hooks.park(context.engagement, hypothesis_id, reason))


@SERVER.tool(
    "ledger.revive",
    "Reopen a parked hypothesis because new evidence bears on it. Name the evidence.",
    {"properties": {"hypothesis_id": {"type": "string"}, "reason": {"type": "string"}},
     "required": ["hypothesis_id", "reason"]}, tier=config.TIER_PASSIVE, touches_target=False,
)
def revive(context: ToolContext, hypothesis_id: str, reason: str) -> dict:
    return _outcome(hooks.revive(context.engagement, hypothesis_id, reason))


@SERVER.tool(
    "ledger.falsify",
    "Close a hypothesis on an observation. The evidence id is required: an opinion, a schedule and "
    "a better idea are reasons to park, not to close.",
    {"properties": {"hypothesis_id": {"type": "string"}, "evidence_id": {"type": "string"},
                    "reason": {"type": "string"}},
     "required": ["hypothesis_id", "evidence_id", "reason"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def falsify(context: ToolContext, hypothesis_id: str, evidence_id: str, reason: str) -> dict:
    return _outcome(hooks.falsify(context.engagement, hypothesis_id, evidence_id, reason))


@SERVER.tool(
    "ledger.add_evidence",
    "Record an observation this broker did not produce: a request from a proxy, a browser result, "
    "a source-code read, a screenshot, a callback seen elsewhere. This is how an external tool — "
    "Burp, a playwright session, a hand-written script — contributes evidence that the proof matrix "
    "will grade on equal terms. Use the field names the matrix reads: nonce, executed, actor, "
    "accessed_subject, token_accepted, phase, is_control, extracted.",
    {"properties": {
        "kind": {"type": "string",
                 "enum": ["probe", "control", "oob", "browser", "source", "artifact"]},
        "target": {"type": "string"},
        "vuln_class": {"type": "string"},
        "hypothesis_id": {"type": "string"},
        "record": {"type": "object", "description": "the evidence fields themselves"},
    }, "required": ["kind", "record"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def add_evidence(context: ToolContext, kind: str, record: dict, target: str = "",
                 vuln_class: str = "", hypothesis_id: str = "") -> dict:
    state = context.state
    payload = dict(record or {})
    payload.update({"kind": kind})
    if target:
        payload["target"] = target
    if vuln_class:
        payload["vuln_class"] = vuln_class
    if hypothesis_id:
        payload["hypothesis_id"] = hypothesis_id
    stored = state.add_evidence(payload)
    state.save()
    return {"summary": f"evidence {stored['id']} recorded ({kind})",
            "data": {"evidence_id": stored["id"]},
            "next": "grade it with proof.verify before trying to record a finding"}


@SERVER.tool(
    "ledger.read_evidence",
    "Read evidence records back in full. Use it to check what is actually recorded before claiming "
    "anything from it.",
    {"properties": {"evidence_ids": {"type": "array"}, "hypothesis_id": {"type": "string"},
                    "limit": {"type": "integer"}},
     "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def read_evidence(context: ToolContext, evidence_ids: list | None = None,
                  hypothesis_id: str = "", limit: int = 5) -> dict:
    state = context.state
    records = (state.load_evidence([str(i) for i in evidence_ids]) if evidence_ids
               else state.evidence_for(hypothesis_id=hypothesis_id or None))
    records = records[: max(1, min(int(limit), 20))]
    return {"summary": f"{len(records)} evidence record(s)",
            "data": {"records": records},
            "output": json.dumps(records, ensure_ascii=False, indent=2)[:12000]}


@SERVER.tool(
    "ledger.record_finding",
    "Record a finding. The evidence is graded against the class's proof requirement first: `proven` "
    "is stored as confirmed, `supported` is stored as a candidate with the missing check named, and "
    "`unproven` is refused outright. This is the gate that stops an agent reporting a vulnerability "
    "it did not demonstrate.",
    {"properties": {
        "hypothesis_id": {"type": "string"},
        "title": {"type": "string"},
        "evidence_ids": {"type": "array"},
        "impact": {"type": "string", "description": "what an attacker gains, concretely"},
        "remediation": {"type": "string"},
        "reproduce": {"type": "array", "description": "the exact steps, in order"},
        "severity": {"type": "string",
                     "enum": ["critical", "high", "medium", "low", "info"]},
    }, "required": ["hypothesis_id", "title", "evidence_ids"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def record_finding(context: ToolContext, hypothesis_id: str, title: str, evidence_ids: list,
                   impact: str = "", remediation: str = "", reproduce: list | None = None,
                   severity: str = "") -> dict:
    outcome = hooks.record_finding(context.engagement, hypothesis_id, title,
                                   [str(i) for i in evidence_ids], impact, remediation,
                                   reproduce, severity or None, actor=context.actor)
    return _outcome(outcome, extra_next=(
        "have a model from a different family check it with ledger.cross_verify" if outcome.ok
        else "read the proof block: it names the check that is missing"))


@SERVER.tool(
    "ledger.cross_verify",
    "Record a second model's reading of a finding's evidence. Disagreement demotes a confirmed "
    "finding to a candidate — which is the correct outcome, not a failure.",
    {"properties": {"finding_id": {"type": "string"}, "verifier": {"type": "string"},
                    "agrees": {"type": "boolean"}, "note": {"type": "string"}},
     "required": ["finding_id", "verifier", "agrees"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def cross_verify(context: ToolContext, finding_id: str, verifier: str, agrees: bool,
                 note: str = "") -> dict:
    return _outcome(hooks.cross_verify(context.engagement, finding_id, verifier, agrees, note))


@SERVER.tool(
    "ledger.strategy",
    "Mark an escalation strategy as spent, so the controller offers the next one instead of the "
    "same one. The rungs are reuse_known_chain, reclassify_surface, research_target_stack, "
    "widen_surface, fleet_sweep, operator_handoff.",
    {"properties": {"rung": {"type": "string"}}, "required": ["rung"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def strategy(context: ToolContext, rung: str) -> dict:
    return _outcome(hooks.strategy(context.engagement, rung))


@SERVER.tool(
    "ledger.report",
    "Render the report: confirmed findings with the checks behind them, candidates with the exact "
    "missing check, hypotheses that were parked or falsified, and a coverage section that states "
    "what was not tested.",
    {"properties": {"write": {"type": "boolean", "description": "also write report.md"}},
     "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def report(context: ToolContext, write: bool = False) -> dict:
    text = report_mod.render(context.engagement)
    path = report_mod.write(context.engagement) if write else None
    return {"summary": f"report rendered ({len(text)} chars)" + (f" to {path}" if path else ""),
            "data": {"path": path}, "output": text[:20000]}
