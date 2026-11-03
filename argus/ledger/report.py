"""Render the engagement into a report that distinguishes proof from opinion.

Three sections, in this order and never merged:

1. **Confirmed** — the proof requirement was met. Each one prints the checks
   that passed and the evidence ids behind them, so a reader can audit it.
2. **Candidates** — a real signal with a named missing check. This section is
   the useful one for the next session: it says exactly what to go and get.
3. **Not demonstrated** — hypotheses that were parked or falsified, with the
   observation that closed them.

Then coverage: what was measured, what was not, and what the engagement was
blind to. An absence stated with its boundary is worth more than a confident
claim that does not survive the next session.
"""
from __future__ import annotations

from .. import config
from ..util import now_iso
from . import proof as proof_mod
from .state import State

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4, "n/a": 5}


def render(name: str) -> str:
    state = State.load(name)
    data = state.data
    findings = sorted(data["findings"],
                      key=lambda f: (SEVERITY_ORDER.get((f.get("severity") or "unknown").lower(), 9),
                                     f.get("vuln_class") or ""))
    confirmed = [f for f in findings if f.get("status") == "confirmed"]
    candidates = [f for f in findings if f.get("status") != "confirmed"]
    scope = state.scope
    lines: list[str] = []
    add = lines.append

    add(f"# {data['engagement']} — penetration test report")
    add("")
    add(f"*Objective:* {data['objective'] or 'not stated'}")
    add(f"*Opened:* {data['created']}  ·  *Rendered:* {now_iso()}  ·  *Status:* {data['status']}")
    roe = data["rules_of_engagement"]
    add(f"*Risk tiers enabled:* {', '.join(roe.get('tiers') or [])}")
    add(f"*Authorisation on file:* {roe.get('authorisation') or '**none recorded**'}")
    add("")
    add("## Scope")
    add("")
    add("| In scope | Out of scope | Ports |")
    add("|---|---|---|")
    add(f"| {', '.join(scope.in_scope) or '—'} | {', '.join(scope.out_of_scope) or '—'} | "
        f"{', '.join(str(p) for p in scope.allowed_ports) or 'any'} |")
    add("")
    add(f"Targets admitted: {', '.join(data['targets']) or 'none'}")
    add("")

    add("## Summary")
    add("")
    add(f"- **{len(confirmed)} confirmed** finding(s): the class's proof requirement was met.")
    add(f"- **{len(candidates)} candidate(s)**: a real signal, with the missing check named below.")
    add(f"- {len(data['probes'])} probe(s) recorded across "
        f"{len({p['vuln_class'] for p in data['probes']})} class(es).")
    add(f"- {len([h for h in data['hypotheses'] if h['status'] == 'falsified'])} hypothesis(es) "
        f"falsified by observation, "
        f"{len([h for h in data['hypotheses'] if h['status'] == 'parked'])} parked.")
    add("")

    if confirmed:
        add("## Confirmed findings")
        add("")
        for finding in confirmed:
            _finding_block(add, state, finding, confirmed=True)
    if candidates:
        add("## Candidates — a signal without a complete proof")
        add("")
        add("Each entry names the one check that is missing. None of these may be reported as a "
            "vulnerability until that check is recorded.")
        add("")
        for finding in candidates:
            _finding_block(add, state, finding, confirmed=False)

    closed = [h for h in data["hypotheses"] if h["status"] in ("falsified", "parked")]
    if closed:
        add("## Not demonstrated")
        add("")
        add("| Class | Target | Status | Closed by | Revive when |")
        add("|---|---|---|---|---|")
        for hypothesis in closed:
            closed_by = (hypothesis.get("closed_by") or {}).get("reason") or "—"
            add(f"| {hypothesis['vuln_class']} | {hypothesis['target']} | {hypothesis['status']} | "
                f"{closed_by} | {hypothesis.get('falsifier') or '—'} |")
        add("")

    add("## Coverage and limits")
    add("")
    surface = state.digest()["surface_counts"]
    add("- Surface mapped: " + (", ".join(f"{count} {kind}" for kind, count in surface.items())
                                or "nothing") + ".")
    budget = state.budget()
    add(f"- Probe budget: {budget.probes} of {budget.probe_limit} probes and "
        f"{budget.minutes:.0f} of {budget.minute_limit:.0f} active minutes used.")
    add(f"- Strategies spent: {', '.join(data['strategies_used']) or 'none'}; "
        f"next unspent: {state.next_strategy() or 'none — the ladder is exhausted'}.")
    untested = _untested_classes(state)
    if untested:
        add(f"- Classes with no hypothesis on any target: {', '.join(untested)}. Their absence from "
            f"this report is an absence of testing, not an absence of risk.")
    add("- Denial of service was not tested: this system refuses that class by construction, "
        "because the proof is the damage.")
    add("- Every command issued is in `log/commands.jsonl`; every observation is in `evidence/`.")
    add("")
    add("## Method")
    add("")
    add("Findings in this report were produced by an LLM-driven agent constrained by an external "
        "ledger. The agent could not reach a target outside the scope above, could not run a "
        "command above the enabled risk tier, and could not record a finding whose evidence did "
        "not satisfy the class's proof requirement. Code execution was demonstrated with "
        "`id; echo <nonce>` and nothing else.")
    return "\n".join(lines) + "\n"


def _finding_block(add, state: State, finding: dict, confirmed: bool) -> None:
    spec = proof_mod.spec_for(finding.get("vuln_class") or "")
    add(f"### {finding.get('title') or finding['id']}")
    add("")
    add(f"| | |")
    add(f"|---|---|")
    add(f"| id | `{finding['id']}` |")
    add(f"| class | {finding.get('vuln_class')} |")
    add(f"| severity | {finding.get('severity')} |")
    add(f"| target | {finding.get('target')} |")
    entry = finding.get("entry_point") or {}
    if entry:
        add(f"| entry point | {', '.join(f'{k}={v}' for k, v in entry.items())} |")
    proof = finding.get("proof") or {}
    add(f"| proof grade | **{proof.get('grade')}** ({proof.get('kind')}) |")
    add(f"| evidence | {', '.join(f'`{e}`' for e in finding.get('evidence_ids') or [])} |")
    verifications = finding.get("verified_by") or []
    if verifications:
        add(f"| cross-verified | " + "; ".join(
            f"{v['verifier']}: {'agrees' if v['agrees'] else 'disagrees'}" for v in verifications) + " |")
    add("")
    if spec:
        add(f"**Requirement:** {spec.requirement}")
        add("")
    for check in proof.get("checks") or []:
        mark = "x" if check["ok"] else " "
        add(f"- [{mark}] {check['check']}" + (f" — {check['detail']}" if check.get("detail") else ""))
    add("")
    if not confirmed and proof.get("missing"):
        add(f"**Missing for a proof:** {', '.join(proof['missing'])}")
        add("")
    if finding.get("impact"):
        add(f"**Impact.** {finding['impact']}")
        add("")
    if finding.get("reproduce"):
        add("**Reproduce.**")
        add("")
        add("```")
        for step in finding["reproduce"]:
            add(str(step))
        add("```")
        add("")
    if finding.get("remediation"):
        add(f"**Remediation.** {finding['remediation']}")
        add("")


def _untested_classes(state: State) -> list[str]:
    from ..knowledge import playbook
    tried = {h["vuln_class"] for h in state.data["hypotheses"]}
    return [c for c in playbook.known_classes() if c not in tried]


def write(name: str) -> str:
    state = State.load(name)
    text = render(name)
    state.paths.report.parent.mkdir(parents=True, exist_ok=True)
    state.paths.report.write_text(text, encoding="utf-8")
    state.event("report.written", {"path": str(state.paths.report), "bytes": len(text)})
    return str(state.paths.report)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="argus-report")
    parser.add_argument("engagement")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        print(write(args.engagement))
    else:
        print(render(args.engagement))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
