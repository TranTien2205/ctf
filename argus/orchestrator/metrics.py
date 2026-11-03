"""Read the instrumentation back: what an engagement cost, and what it bought.

These are the numbers the design claims rest on. They are computed from what was
recorded rather than from a summary anyone wrote, which is the only way a claim
like "routing beats one strong model" can be settled rather than argued.

Nothing here is a score. A number without its baseline is a number, and the
baseline is the other run — `--deterministic`, a different `--policy`, a pinned
`--model`, or the same targets with the proof requirement switched off.
"""
from __future__ import annotations

import json
from collections import Counter

from .. import config
from ..ledger.state import State
from ..util import read_json, read_jsonl


def collect(engagement: str) -> dict:
    state = State.load(engagement)
    paths = state.paths
    data = state.data
    findings = data["findings"]
    confirmed = [f for f in findings if f.get("status") == "confirmed"]
    candidates = [f for f in findings if f.get("status") != "confirmed"]
    probes = data["probes"]
    cost_lines = read_jsonl(paths.cost)
    refusals = read_jsonl(paths.refusals)
    commands = read_jsonl(paths.commands)
    plan = read_json(paths.plan, {}) or {}
    tasks = plan.get("tasks") or []

    by_model: dict[str, dict] = {}
    for line in cost_lines:
        entry = by_model.setdefault(line.get("model") or "?",
                                    {"calls": 0, "cost_usd": 0.0, "input_tokens": 0,
                                     "output_tokens": 0})
        entry["calls"] += 1
        entry["cost_usd"] += float(line.get("cost_usd") or 0.0)
        entry["input_tokens"] += int(line.get("input_tokens") or 0)
        entry["output_tokens"] += int(line.get("output_tokens") or 0)
    for task in tasks:
        result = task.get("result") or {}
        model = result.get("model") or (task.get("route") or {}).get("model")
        if not model or result.get("cost_usd") in (None, 0) or model in by_model:
            continue
        by_model.setdefault(model, {"calls": 0, "cost_usd": 0.0, "input_tokens": 0,
                                    "output_tokens": 0})
        by_model[model]["cost_usd"] += float(result.get("cost_usd") or 0.0)

    total_cost = sum(entry["cost_usd"] for entry in by_model.values()) or sum(
        float((task.get("result") or {}).get("cost_usd") or 0.0) for task in tasks)
    probes_by_class = Counter(probe["vuln_class"] for probe in probes)
    steps_by_class: dict[str, set] = {}
    for probe in probes:
        steps_by_class.setdefault(probe["vuln_class"], set()).add(probe.get("step") or probe["tool"])

    # A class probed many times through few distinct ladder steps is the shape of
    # an agent re-asking the same question with a new payload.
    repeat_ratio = {}
    for vuln_class, count in probes_by_class.items():
        distinct = max(1, len(steps_by_class.get(vuln_class) or {1}))
        repeat_ratio[vuln_class] = round(count / distinct, 2)

    return {
        "engagement": engagement,
        "objective": data["objective"],
        "findings": {"confirmed": len(confirmed), "candidates": len(candidates),
                     "by_class": dict(Counter(f.get("vuln_class") for f in findings)),
                     "cross_verified": len([f for f in findings if f.get("verified_by")]),
                     "demoted_by_review": len([f for f in findings if f.get("demotions")])},
        "effort": {
            "probes": len(probes),
            "probes_by_class": dict(probes_by_class),
            # Only the tools that shell out to another binary appear here; the HTTP
            # tools issue requests in-process, so this is a subset of tool calls
            # rather than a count of them.
            "external_commands": len(commands),
            "repeat_ratio_by_class": repeat_ratio,
            "hypotheses": dict(Counter(h["status"] for h in data["hypotheses"])),
            "active_minutes": round(state.active_minutes(probes), 1),
        },
        "refusals": {"total": len(refusals),
                     "by_kind": dict(Counter(r.get("refusal") for r in refusals)),
                     "by_tool": dict(Counter(r.get("tool") for r in refusals).most_common(8)),
                     "out_of_scope_attempts": len([r for r in refusals
                                                   if r.get("refusal") == "out-of-scope"])},
        "cost": {
            "total_usd": round(total_cost, 4),
            "by_model": {model: {**entry, "cost_usd": round(entry["cost_usd"], 4)}
                         for model, entry in sorted(by_model.items())},
            "per_confirmed_finding_usd": (round(total_cost / len(confirmed), 4)
                                          if confirmed else None),
            "probes_per_confirmed_finding": (round(len(probes) / len(confirmed), 1)
                                             if confirmed else None),
        },
        "plan": {"created_by": plan.get("created_by"), "tasks": len(tasks),
                 "by_status": dict(Counter(task.get("status") for task in tasks)),
                 "by_kind": dict(Counter(task.get("kind") for task in tasks)),
                 "by_model": dict(Counter((task.get("route") or {}).get("model")
                                          for task in tasks if task.get("route")))},
    }


def render(metrics: dict) -> str:
    lines = [f"{metrics['engagement']} — {metrics['objective'] or '(no objective)'}", ""]
    findings = metrics["findings"]
    lines.append(f"findings: {findings['confirmed']} confirmed, {findings['candidates']} "
                 f"candidate(s), {findings['cross_verified']} cross-verified, "
                 f"{findings['demoted_by_review']} demoted by review")
    if findings["by_class"]:
        lines.append(f"  by class: {findings['by_class']}")
    effort = metrics["effort"]
    lines.append(f"effort: {effort['probes']} probe(s), {effort['external_commands']} external "
                 f"command(s) (nmap/ffuf/sqlmap and the like; the HTTP tools do not shell out), "
                 f"{effort['active_minutes']} active minute(s)")
    lines.append(f"  hypotheses: {effort['hypotheses']}")
    high = {k: v for k, v in effort["repeat_ratio_by_class"].items() if v >= 3}
    if high:
        lines.append(f"  probes per distinct ladder step, 3 or more: {high}  "
                     f"<- the shape of re-asking the same question with a new payload")
    refusals = metrics["refusals"]
    lines.append(f"refusals: {refusals['total']} ({refusals['by_kind'] or 'none'})")
    lines.append(f"  attempts outside the declared scope: {refusals['out_of_scope_attempts']}")
    cost = metrics["cost"]
    lines.append(f"cost: ${cost['total_usd']:.4f}"
                 + (f", ${cost['per_confirmed_finding_usd']:.4f} per confirmed finding"
                    if cost["per_confirmed_finding_usd"] is not None else
                    ", no confirmed finding to divide by"))
    for model, entry in cost["by_model"].items():
        lines.append(f"  {model:26} {entry['calls']:4} call(s)  ${entry['cost_usd']:.4f}  "
                     f"{entry['input_tokens'] + entry['output_tokens']} tokens")
    plan = metrics["plan"]
    if plan["tasks"]:
        lines.append(f"plan by {plan['created_by']}: {plan['tasks']} task(s) {plan['by_status']}")
        lines.append(f"  routed to: {plan['by_model']}")
    if cost["probes_per_confirmed_finding"] is not None:
        lines.append(f"\nprobes per confirmed finding: {cost['probes_per_confirmed_finding']}")
    lines.append("\nA number here means nothing without its baseline run. See ARCHITECTURE.md "
                 "section 6 for which baseline each claim needs.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="argus-metrics", description=__doc__.splitlines()[0])
    parser.add_argument("engagement")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    metrics = collect(args.engagement)
    print(json.dumps(metrics, ensure_ascii=False, indent=2) if args.json else render(metrics))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
