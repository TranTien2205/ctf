"""The only write path into the ledger.

Everything above this module *proposes*. This module decides, and a refusal is
a normal, named outcome rather than an error. Six refusals exist, and each one
exists because the same mistake was cheap to make and expensive to notice:

    out-of-scope        the target matched no in-scope rule, or matched a deny
    tier-not-enabled    the command's risk tier is not in the rules of engagement
    class-mismatch      the probe's class does not match the hypothesis it names
    budget-spent        this class has had its probes; change strategy, not payload
    unproven            the evidence does not meet the class's proof requirement
    refused-class       the class may not be proven by this system at all

The sixth is the one that matters most for an autonomous tester: a model that
cannot record a finding without proof stops producing confident prose about
vulnerabilities it never demonstrated.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

from .. import config
from ..util import now_iso
from . import proof as proof_mod
from .lock import engagement_lock
from .state import CONFIRMED, FALSIFIED, OPEN, PARKED, RECON, State


def _log_refusal(name: str, outcome: "Outcome") -> None:
    """Every refusal, on disk, once.

    `argus metrics` reads this log, and claim 1 in ARCHITECTURE.md section 6 is
    "how many unproven claims the gate turned away" — which was unreportable
    while refusals existed only in the return value. The broker used to log the
    pre-probe refusals itself; it no longer does, because two writers for one
    number is how a measurement quietly doubles.
    """
    if outcome.ok:
        return
    try:
        from ..util import append_jsonl, bound, now_iso
        append_jsonl(config.Paths(name).refusals, {
            "ts": now_iso(), "source": "ledger", "verb": outcome.verb,
            "refusal": outcome.refusal, "message": bound(outcome.message, 400),
            "target": outcome.data.get("target"), "vuln_class": outcome.data.get("class"),
            "hypothesis_id": outcome.data.get("hypothesis"),
        })
    except (ValueError, OSError):
        pass


def _logs(verb):
    """Record a refusal from a read-only verb."""
    import functools

    @functools.wraps(verb)
    def wrapper(name, *args, **kwargs):
        outcome = verb(name, *args, **kwargs)
        _log_refusal(name, outcome)
        return outcome
    return wrapper


def _locked(verb):
    """Serialise one verb's load-mutate-save against other agents, and record a
    refusal if it refuses."""
    import functools

    @functools.wraps(verb)
    def wrapper(name, *args, **kwargs):
        try:
            directory = config.Paths(name).dir
        except ValueError:
            return verb(name, *args, **kwargs)
        with engagement_lock(directory):
            outcome = verb(name, *args, **kwargs)
        _log_refusal(name, outcome)
        return outcome
    return wrapper


@dataclass
class Outcome:
    ok: bool
    verb: str
    refusal: str | None = None
    message: str = ""
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        out = {"ok": self.ok, "verb": self.verb, "message": self.message}
        if self.refusal:
            out["refusal"] = self.refusal
        out.update(self.data)
        return out

    def __bool__(self) -> bool:
        return self.ok


def _refuse(verb: str, refusal: str, message: str, **data) -> Outcome:
    return Outcome(False, verb, refusal, message, data)


# --- engagement --------------------------------------------------------------

def open_engagement(name: str, objective: str, scope: dict, tiers: list[str] | None = None,
                    authorisation: str | None = None) -> Outcome:
    tiers = list(tiers or [config.TIER_PASSIVE, config.TIER_ACTIVE])
    unknown = [t for t in tiers if t not in config.TIERS]
    if unknown:
        return _refuse("open", "tier-not-enabled", f"unknown risk tier(s): {unknown}")
    if config.TIER_INTRUSIVE in tiers and not authorisation:
        return _refuse("open", "tier-not-enabled",
                       "the intrusive tier needs an --authorisation note naming who authorised it "
                       "and over what window; a tester's own assertion is not authorisation")
    if not (scope or {}).get("in_scope"):
        return _refuse("open", "out-of-scope",
                       "in_scope is empty, and an empty scope allows nothing. Name the hosts, "
                       "CIDRs or URL prefixes this engagement covers")
    state = State.create(name, objective=objective, scope=scope, tiers=tiers,
                         authorisation=authorisation)
    return Outcome(True, "open", message=f"engagement {name} opened at {state.paths.dir}",
                   data={"engagement": name, "dir": str(state.paths.dir), "tiers": tiers})


@_locked
def add_target(name: str, target: str, note: str = "") -> Outcome:
    state = State.load(name)
    verdict = state.scope.check(target)
    if not verdict:
        return _refuse("add-target", "out-of-scope", verdict.reason, target=target)
    state.add_target(target, note)
    state.save()
    state.event("target.added", {"target": target, "rule": verdict.rule})
    return Outcome(True, "add-target", message=f"{target} is in scope via {verdict.rule}",
                   data={"target": target})


# --- the probe gate ----------------------------------------------------------

@_logs
def pre_probe(name: str, hypothesis_id: str, vuln_class: str, target: str,
              tier: str = config.TIER_ACTIVE, tool: str = "") -> Outcome:
    """Called before every command that touches a target. The brake."""
    state = State.load(name)
    verdict = state.scope.check(target)
    if not verdict:
        return _refuse("pre-probe", "out-of-scope", verdict.reason, target=target)
    if tier not in state.tiers:
        return _refuse("pre-probe", "tier-not-enabled",
                       f"tool {tool or '?'} is {tier}; this engagement enables {state.tiers}",
                       target=target, tier=tier)
    if vuln_class == RECON or hypothesis_id == RECON:
        if vuln_class != RECON or hypothesis_id not in (RECON, None, ""):
            return _refuse("pre-probe", "class-mismatch",
                           "recon probes must declare class 'recon' and hypothesis 'recon'")
        recon_budget = state.budget(RECON, target)
        recon_budget.probe_limit = config.PROBE_BUDGET_RECON
        if recon_budget.probes >= config.PROBE_BUDGET_RECON:
            return _refuse("pre-probe", "budget-spent",
                           f"{recon_budget.probes} recon commands against {target}; the surface is "
                           f"mapped, so classify it instead of mapping it again",
                           budget=recon_budget.to_dict())
        return Outcome(True, "pre-probe", message="recon probe allowed",
                       data={"hypothesis": RECON, "class": RECON,
                             "class_budget": recon_budget.to_dict()})
    hypothesis = state.hypothesis(hypothesis_id)
    if hypothesis is None:
        return _refuse("pre-probe", "class-mismatch",
                       f"no hypothesis {hypothesis_id!r}. Open one first: a probe that names no "
                       f"hypothesis cannot falsify anything")
    if hypothesis["vuln_class"] != vuln_class:
        return _refuse("pre-probe", "class-mismatch",
                       f"hypothesis {hypothesis_id} is about {hypothesis['vuln_class']}, "
                       f"the probe declares {vuln_class}")
    if hypothesis["status"] not in (OPEN,):
        return _refuse("pre-probe", "class-mismatch",
                       f"hypothesis {hypothesis_id} is {hypothesis['status']}; revive it before probing")
    class_budget = state.budget(vuln_class, target)
    if class_budget.spent:
        rung = state.next_strategy()
        return _refuse("pre-probe", "budget-spent",
                       f"{class_budget.probes} probes and {class_budget.minutes:.0f} active minutes "
                       f"on {vuln_class}@{target}. Park it and climb the ladder instead"
                       + (f": next rung is {rung}" if rung else ": the ladder is spent, hand off"),
                       budget=class_budget.to_dict(), next_strategy=rung)
    target_budget = state.budget(target=target)
    if target_budget.spent:
        return _refuse("pre-probe", "budget-spent",
                       f"{target_budget.probes} probes on {target} across every class; widen the "
                       f"surface or hand off rather than probing more",
                       budget=target_budget.to_dict())
    return Outcome(True, "pre-probe", message="probe allowed",
                   data={"hypothesis": hypothesis_id, "class": vuln_class,
                         "class_budget": class_budget.to_dict(),
                         "target_budget": target_budget.to_dict()})


@_locked
def post_probe(name: str, hypothesis_id: str, vuln_class: str, target: str, tool: str,
               command, result: str, evidence: dict | None = None,
               duration_ms: int | None = None, exit_code: int | None = None,
               actor: str = "main", step: str = "") -> Outcome:
    """Record what the probe observed. One probe, one evidence record, always."""
    state = State.load(name)
    if result not in ("signal", "no-signal", "error", "refused"):
        return _refuse("post-probe", "class-mismatch",
                       "result must be signal, no-signal, error or refused")
    if vuln_class != RECON:
        hypothesis = state.hypothesis(hypothesis_id)
        if hypothesis is None:
            return _refuse("post-probe", "class-mismatch", f"no hypothesis {hypothesis_id!r}")
        if hypothesis["vuln_class"] != vuln_class:
            return _refuse("post-probe", "class-mismatch",
                           f"hypothesis {hypothesis_id} is about {hypothesis['vuln_class']}")
    record = None
    if evidence:
        payload = dict(evidence)
        payload.setdefault("vuln_class", vuln_class)
        payload.setdefault("target", target)
        payload.setdefault("hypothesis_id", hypothesis_id)
        payload.setdefault("tool", tool)
        record = state.add_evidence(payload)
    probe = state.record_probe(hypothesis_id, vuln_class, target, tool, command, result,
                               record["id"] if record else None, duration_ms, exit_code, actor, step)
    state.save()
    state.event("probe.recorded", {"probe": probe["id"], "class": vuln_class, "result": result,
                                   "evidence": record["id"] if record else None}, actor=actor)
    return Outcome(True, "post-probe", message=f"probe {probe['id']} recorded",
                   data={"probe": probe["id"], "evidence": record["id"] if record else None,
                         "class_budget": state.budget(vuln_class, target).to_dict()})


# --- closing a hypothesis ----------------------------------------------------

@_locked
def falsify(name: str, hypothesis_id: str, evidence_id: str, reason: str) -> Outcome:
    """A hypothesis closes on an observation, never on an opinion."""
    state = State.load(name)
    if not state.load_evidence([evidence_id]):
        return _refuse("falsify", "unproven",
                       f"no evidence {evidence_id!r}; a hypothesis is closed by an observation")
    if not reason.strip():
        return _refuse("falsify", "unproven", "name the observation that falsifies it")
    state.set_hypothesis_status(hypothesis_id, FALSIFIED, reason, evidence_id)
    state.save()
    state.event("hypothesis.falsified", {"hypothesis": hypothesis_id, "evidence": evidence_id,
                                         "reason": reason})
    return Outcome(True, "falsify", message=f"{hypothesis_id} falsified")


@_locked
def park(name: str, hypothesis_id: str, reason: str) -> Outcome:
    """Park, do not delete. A direction that looks wrong is usually unfinished."""
    state = State.load(name)
    if state.hypothesis(hypothesis_id) is None:
        return _refuse("park", "class-mismatch", f"no hypothesis {hypothesis_id!r}")
    state.set_hypothesis_status(hypothesis_id, PARKED, reason or "parked")
    state.save()
    state.event("hypothesis.parked", {"hypothesis": hypothesis_id, "reason": reason})
    return Outcome(True, "park", message=f"{hypothesis_id} parked at priority 0, revivable")


@_locked
def revive(name: str, hypothesis_id: str, reason: str) -> Outcome:
    state = State.load(name)
    if state.hypothesis(hypothesis_id) is None:
        return _refuse("revive", "class-mismatch", f"no hypothesis {hypothesis_id!r}")
    state.revive_hypothesis(hypothesis_id, reason)
    state.save()
    state.event("hypothesis.revived", {"hypothesis": hypothesis_id, "reason": reason})
    return Outcome(True, "revive", message=f"{hypothesis_id} reopened")


# --- the finding gate --------------------------------------------------------

@_locked
def record_finding(name: str, hypothesis_id: str, title: str, evidence_ids: list[str],
                   impact: str = "", remediation: str = "", reproduce: list[str] | None = None,
                   severity: str | None = None, actor: str = "main") -> Outcome:
    """Verify the evidence against the class's proof requirement, then record.

    `proven` becomes a confirmed finding. `supported` is recorded as a candidate
    with its missing checks named, so the next session knows exactly what to go
    and get. `unproven` and `refused` are not recorded at all.
    """
    state = State.load(name)
    hypothesis = state.hypothesis(hypothesis_id)
    if hypothesis is None:
        return _refuse("record-finding", "class-mismatch", f"no hypothesis {hypothesis_id!r}")
    vuln_class = hypothesis["vuln_class"]
    records = state.load_evidence(evidence_ids)
    missing_ids = [eid for eid in evidence_ids if eid not in {r.get("id") for r in records}]
    if missing_ids:
        return _refuse("record-finding", "unproven", f"evidence not found: {missing_ids}")
    verdict = proof_mod.verify(vuln_class, records)
    if verdict.grade == "refused":
        return _refuse("record-finding", "refused-class", verdict.requirement or
                       f"{vuln_class} may not be proven by this system",
                       proof=verdict.to_dict())
    if verdict.grade == "unproven":
        return _refuse("record-finding", "unproven",
                       f"nothing in the {len(records)} evidence record(s) meets the requirement for "
                       f"{vuln_class}: {verdict.requirement}", proof=verdict.to_dict())
    spec = proof_mod.spec_for(vuln_class)
    finding = state.add_finding({
        "vuln_class": vuln_class,
        "title": title,
        "status": "confirmed" if verdict.proven else "candidate",
        "severity": severity or (spec.severity if spec else "unknown"),
        "target": hypothesis["target"],
        "entry_point": hypothesis["entry_point"],
        "hypothesis_id": hypothesis_id,
        "evidence_ids": evidence_ids,
        "proof": verdict.to_dict(),
        "reproduce": reproduce or [],
        "impact": impact,
        "remediation": remediation,
        "recorded_by": actor,
        "verified_by": [],
    })
    if verdict.proven:
        state.set_hypothesis_status(hypothesis_id, CONFIRMED, "proof requirement met",
                                   evidence_ids[0] if evidence_ids else None)
        hypothesis["finding_id"] = finding["id"]
    state.save()
    state.event("finding.recorded", {"finding": finding["id"], "class": vuln_class,
                                     "grade": verdict.grade}, actor=actor)
    return Outcome(True, "record-finding",
                   message=f"{finding['id']} recorded as {finding['status']} ({verdict.grade})",
                   data={"finding": finding["id"], "proof": verdict.to_dict()})


@_locked
def cross_verify(name: str, finding_id: str, verifier: str, agrees: bool, note: str = "") -> Outcome:
    """A second model, from a different family, says whether the evidence carries
    the claim. Disagreement demotes a confirmed finding back to a candidate."""
    state = State.load(name)
    finding = state.finding(finding_id)
    if finding is None:
        return _refuse("cross-verify", "class-mismatch", f"no finding {finding_id!r}")
    finding["verified_by"].append({"verifier": verifier, "agrees": bool(agrees),
                                   "note": note, "ts": now_iso()})
    if not agrees and finding["status"] == "confirmed":
        finding["status"] = "candidate"
        finding.setdefault("demotions", []).append({"by": verifier, "note": note, "ts": now_iso()})
    state.save()
    state.event("finding.cross-verified", {"finding": finding_id, "verifier": verifier,
                                           "agrees": bool(agrees)})
    return Outcome(True, "cross-verify", message=f"{finding_id} is now {finding['status']}",
                   data={"status": finding["status"]})


@_locked
def strategy(name: str, rung: str) -> Outcome:
    state = State.load(name)
    if rung not in __import__("argus.ledger.state", fromlist=["LADDER"]).LADDER:
        return _refuse("strategy", "class-mismatch", f"{rung!r} is not a rung on the ladder")
    state.strategy_used(rung)
    state.save()
    state.event("strategy.used", {"rung": rung})
    return Outcome(True, "strategy", message=f"{rung} marked spent",
                   data={"next_strategy": state.next_strategy()})


@_locked
def close_engagement(name: str, note: str = "") -> Outcome:
    state = State.load(name)
    state.data["status"] = "closed"
    state.data["notes"].append({"ts": now_iso(), "note": note or "closed"})
    state.save()
    state.event("engagement.closed", {"note": note})
    return Outcome(True, "close", message=f"{name} closed")


# --- CLI ---------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="argus-hooks", description=__doc__.splitlines()[0])
    parser.add_argument("verb", choices=["open", "add-target", "pre-probe", "post-probe", "falsify",
                                         "park", "revive", "record-finding", "cross-verify",
                                         "strategy", "close"])
    parser.add_argument("engagement")
    parser.add_argument("--json", dest="payload", default="{}",
                        help="verb arguments as a JSON object")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as error:
        print(json.dumps({"ok": False, "refusal": "bad-json", "message": str(error)}))
        return 2
    verbs = {
        "open": open_engagement, "add-target": add_target, "pre-probe": pre_probe,
        "post-probe": post_probe, "falsify": falsify, "park": park, "revive": revive,
        "record-finding": record_finding, "cross-verify": cross_verify, "strategy": strategy,
        "close": close_engagement,
    }
    try:
        outcome = verbs[args.verb](args.engagement, **payload)
    except (TypeError, ValueError, KeyError, FileNotFoundError, FileExistsError) as error:
        print(json.dumps({"ok": False, "verb": args.verb, "refusal": "bad-request",
                          "message": f"{type(error).__name__}: {error}"}, ensure_ascii=False))
        return 2
    print(json.dumps(outcome.to_dict(), ensure_ascii=False, indent=2))
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    sys.exit(main())
