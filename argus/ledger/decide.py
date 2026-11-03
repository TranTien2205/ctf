"""The decision controller: given the ledger, what happens next.

The model does not choose the shape of the next move; it chooses the content.
That split is deliberate. A strong model given a ledger and an open question
will usually pick a reasonable next action — and a weak one, a tired one, or
one whose context has drifted will instead repeat the last command with a new
payload, or write a confident paragraph about a vulnerability it has not shown.
This controller is what makes those two cases indistinguishable from the
outside: the next action is computed from recorded evidence, and the model is
asked to carry it out and to justify any departure from it.

The rules are ordered, fail-closed, and each one names the observation that
triggered it. Rule 10 is the only one that ends an engagement.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

from .. import config
from ..knowledge import playbook
from ..util import read_json
from . import proof as proof_mod
from .state import OPEN, RECON, State


@dataclass
class Action:
    action: str
    why: str
    target: str | None = None
    hypothesis_id: str | None = None
    vuln_class: str | None = None
    step: str | None = None
    tool: str | None = None
    tier: str | None = None
    skill: str | None = None
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        out = {"action": self.action, "why": self.why}
        for key in ("target", "hypothesis_id", "vuln_class", "step", "tool", "tier", "skill"):
            value = getattr(self, key)
            if value:
                out[key] = value
        if self.detail:
            out["detail"] = self.detail
        return out

    def render(self) -> str:
        head = f"NEXT: {self.action}"
        bits = [f"{k}={v}" for k, v in self.to_dict().items() if k not in ("action", "why", "detail")]
        lines = [head + ("  " + " ".join(bits) if bits else ""), f"why: {self.why}"]
        for key, value in (self.detail or {}).items():
            lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)[:400]}")
        return "\n".join(lines)


def _proof_state(state: State, hypothesis: dict,
                 with_evidence: set[str] | None = None) -> proof_mod.ProofVerdict:
    """Grade one hypothesis. The index says whether loading anything is worth it.

    `decide()` runs on every harness step, and loading every evidence file for
    every open hypothesis each time turns a cheap decision into a few hundred
    reads. The index already knows which hypotheses have records.
    """
    if with_evidence is not None and hypothesis["id"] not in with_evidence:
        return proof_mod.ProofVerdict(hypothesis["vuln_class"], "unknown", "unproven",
                                      [], ["evidence exists"], "")
    records = state.evidence_for(hypothesis_id=hypothesis["id"])
    return proof_mod.verify(hypothesis["vuln_class"], records)


def decide(name: str) -> Action:
    try:
        state = State.load(name)
    except FileNotFoundError:
        return Action("open_engagement",
                      f"no engagement {name!r} exists. Name the objective, the scope and who "
                      f"authorised it before any command runs.")

    scope = state.scope
    if not scope.in_scope:
        return Action("set_scope", "the scope is empty, and an empty scope allows nothing.")

    if state.data["status"] == "closed":
        return Action("report", "the engagement is closed; write or re-read the report.",
                      detail={"report": str(state.paths.report)})

    targets = list(state.data["targets"])
    if not targets:
        return Action("add_target", "scope is set but no target has been admitted to the ledger.",
                      detail={"in_scope": scope.in_scope})

    with_evidence = {entry.get("hypothesis_id") for entry in state.data["evidence_index"]
                     if entry.get("hypothesis_id")}

    # Rule 1 — evidence that already proves something, not yet recorded.
    for hypothesis in state.data["hypotheses"]:
        if hypothesis["status"] != OPEN or hypothesis.get("finding_id"):
            continue
        verdict = _proof_state(state, hypothesis, with_evidence)
        if verdict.proven:
            return Action("record_finding",
                          f"the evidence on {hypothesis['id']} already meets the proof requirement "
                          f"for {hypothesis['vuln_class']}. Record it before probing anything else.",
                          target=hypothesis["target"], hypothesis_id=hypothesis["id"],
                          vuln_class=hypothesis["vuln_class"],
                          detail={"proof": verdict.to_dict(),
                                  "evidence_ids": [e["id"] for e in
                                                   state.data["evidence_index"]
                                                   if e.get("hypothesis_id") == hypothesis["id"]]})

    # Rule 2 — a confirmed finding no second model has looked at.
    for finding in state.data["findings"]:
        if finding.get("status") == "confirmed" and not finding.get("verified_by"):
            return Action("cross_verify",
                          f"{finding['id']} is confirmed on one model's reading of the evidence. A "
                          f"model from a different family should agree before it reaches a report.",
                          target=finding.get("target"), vuln_class=finding.get("vuln_class"),
                          detail={"finding": finding["id"],
                                  "evidence_ids": finding.get("evidence_ids", [])})

    # Rule 3 — recon the surface of every target before classifying any of it.
    for target in targets:
        done = set(state.steps_done(RECON, target))
        for step in playbook.recon_ladder():
            if step["step"] not in done:
                return Action("recon",
                              f"{target} has no {step['step']} measurement yet: {step['why']}.",
                              target=target, vuln_class=RECON, hypothesis_id=RECON,
                              step=step["step"], tool=step["tool"], tier=step["tier"],
                              detail={"recon_done": sorted(done),
                                      "surface_counts": state.digest()["surface_counts"]})

    # Rule 4 — evidence that nearly proves something: name the gap, go close it.
    for hypothesis in sorted(state.open_hypotheses(), key=lambda h: -h["priority"]):
        verdict = _proof_state(state, hypothesis, with_evidence)
        if verdict.grade == "supported":
            proof_step = playbook.proof_step(hypothesis["vuln_class"])
            return Action("close_proof_gap",
                          f"{hypothesis['vuln_class']} on {hypothesis['target']} is supported but not "
                          f"proven. Missing: {', '.join(verdict.missing) or 'the controls'}.",
                          target=hypothesis["target"], hypothesis_id=hypothesis["id"],
                          vuln_class=hypothesis["vuln_class"],
                          step=(proof_step or {}).get("step"), tool=(proof_step or {}).get("tool"),
                          tier=(proof_step or {}).get("tier"),
                          skill=playbook.skill_for(hypothesis["vuln_class"]),
                          detail={"proof": verdict.to_dict(), "requirement": verdict.requirement})

    # Rule 5 — surface that no hypothesis covers.
    unclassified = _unclassified_surface(state)
    if unclassified and not state.open_hypotheses():
        return Action("classify",
                      f"{len(unclassified)} surface items carry no hypothesis. Name a class and a "
                      f"falsifier for each one worth probing; park the rest explicitly.",
                      detail={"surface": unclassified[:20],
                              "classes": playbook.known_classes()})

    # Rule 6 / 7 — probe the best open hypothesis, or park it and switch.
    for hypothesis in sorted(state.open_hypotheses(), key=lambda h: -h["priority"]):
        budget = state.budget(hypothesis["vuln_class"], hypothesis["target"])
        if budget.spent:
            continue
        step = playbook.next_step(hypothesis["vuln_class"],
                                 state.steps_done(hypothesis["vuln_class"], hypothesis["target"]))
        if step is None:
            step = playbook.proof_step(hypothesis["vuln_class"]) or {}
        return Action("probe",
                      f"{hypothesis['statement']} — next unrun rung: {step.get('step', 'operator choice')}"
                      + (f" ({step['why']})" if step.get("why") else ""),
                      target=hypothesis["target"], hypothesis_id=hypothesis["id"],
                      vuln_class=hypothesis["vuln_class"], step=step.get("step"),
                      tool=step.get("tool"), tier=step.get("tier"),
                      skill=playbook.skill_for(hypothesis["vuln_class"]),
                      detail={"budget": budget.to_dict(), "falsifier": hypothesis.get("falsifier"),
                              "entry_point": hypothesis.get("entry_point"),
                              "steps_done": state.steps_done(hypothesis["vuln_class"],
                                                             hypothesis["target"])})

    spent = [h for h in state.open_hypotheses()
             if state.budget(h["vuln_class"], h["target"]).spent]
    if spent:
        hypothesis = spent[0]
        return Action("park_and_switch",
                      f"{hypothesis['vuln_class']} on {hypothesis['target']} has spent its probe "
                      f"budget without a falsifying observation. Park it at priority 0 — it stays "
                      f"revivable — and open a different class.",
                      target=hypothesis["target"], hypothesis_id=hypothesis["id"],
                      vuln_class=hypothesis["vuln_class"],
                      detail={"budget": state.budget(hypothesis["vuln_class"],
                                                     hypothesis["target"]).to_dict(),
                              "classes_untried": _untried_classes(state, hypothesis["target"])})

    # Rule 8 — nothing open: climb the ladder instead of stopping.
    rung = state.next_strategy()
    if rung:
        return Action("escalate",
                      f"no open hypothesis and no unmapped surface. The cheapest unspent strategy "
                      f"is {rung}.",
                      detail={"rung": rung, "ladder": list(_ladder()),
                              "spent": state.data["strategies_used"],
                              "how": _LADDER_HOW.get(rung, "")})

    # Rule 9 — unclassified surface left, but the ladder is spent.
    if unclassified:
        return Action("classify",
                      "every strategy has been spent, and surface items remain unclassified. "
                      "Classify them or park them by name before reporting.",
                      detail={"surface": unclassified[:20]})

    # Rule 10 — the only exit.
    return Action("report",
                  "every hypothesis is closed or parked, every strategy is spent. Write the report: "
                  "confirmed findings with their proofs, candidates with the exact missing check, "
                  "and parked hypotheses with what would revive them.",
                  detail={"findings": [{"id": f["id"], "class": f.get("vuln_class"),
                                        "status": f.get("status")}
                                       for f in state.data["findings"]],
                          "parked": [h["id"] for h in state.data["hypotheses"]
                                     if h["status"] == "parked"]})


_LADDER_HOW = {
    "reuse_known_chain": "knowledge.chain_match against the stack this target runs",
    "reclassify_surface": "re-read the surface for an input kind the first pass skipped "
                          "(headers, cookies, path segments, file names, websocket frames)",
    "research_target_stack": "read the vendor advisory or the library source for the exact version",
    "widen_surface": "another host, another port, another vhost, a second credential tier",
    "fleet_sweep": "fan several agents out, one per untried class, in one wave",
    "operator_handoff": "hand what is measured to a human with the exact open question",
}


def _ladder():
    from .state import LADDER
    return LADDER


def _unclassified_surface(state: State) -> list[dict]:
    """Surface items that no hypothesis names, as the controller sees them."""
    claimed = set()
    for hypothesis in state.data["hypotheses"]:
        entry = hypothesis.get("entry_point") or {}
        for value in entry.values():
            if isinstance(value, str):
                claimed.add(value)
    out = []
    for item in state.data["surface"]:
        if item["kind"] not in ("param", "endpoint", "form", "port", "header", "cookie"):
            continue
        if item["value"] in claimed:
            continue
        out.append({"id": item["id"], "target": item["target"], "kind": item["kind"],
                    "value": item["value"], "sources": item["sources"]})
    return out


def _untried_classes(state: State, target: str) -> list[str]:
    tried = {h["vuln_class"] for h in state.data["hypotheses"] if h["target"] == target}
    return [c for c in playbook.known_classes() if c not in tried]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="argus-decide", description=__doc__.splitlines()[0])
    parser.add_argument("engagement")
    parser.add_argument("--json", action="store_true", help="machine-readable, for a harness")
    args = parser.parse_args(argv)
    action = decide(args.engagement)
    print(json.dumps(action.to_dict(), ensure_ascii=False, indent=2) if args.json else action.render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
