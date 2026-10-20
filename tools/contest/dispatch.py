#!/usr/bin/env python3
"""How many challenges to run at once, and how wide to fan out each one.

The counter-intuitive measurement this encodes: fanning out wider is not always
faster, and on an easy challenge it is slower.

* One subagent costs 7-10 minutes spawn-to-report, "a floor, not a budget",
  the same whatever the task (ORCHESTRATION.md, measured: 9.7, 10.2, 7.3, 10.2).
* Useful fan-out width is three to six; "ten is a sweep, not a wave"
  (ORCHESTRATION.md).
* An easy challenge's whole time-box is 15-30 minutes
  (skills/ctf-playbook/SKILL.md).

So ten agents against an easy challenge spends its entire budget on one wave of
spawn latency. The win is on the OTHER axis: challenges are stored in fully
separate ledgers and share no budget, so running several at once is free, while
running more probes inside one is exactly what tools/decide.py governs.

Two real ceilings bound the answer:

1. The harness caps concurrent agents at min(16, cpus-2). Past that they queue,
   and a queued agent is serial time wearing a parallel costume.
2. The main thread's attention. ORCHESTRATION.md: never spawn and then wait --
   the main thread must drive a spine of its own, or the parallelism collapses
   back to serial. That is a human-scale limit, not a CPU one, and it is why the
   default here is a small number of challenges rather than the CPU maximum.

This module prints a plan. It spawns nothing and writes no state.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ORCHESTRATION.md: useful width is 3-6, and ten is a sweep rather than a wave.
MIN_USEFUL_WIDTH = 3
MAX_USEFUL_WIDTH = 6
# A strong chain card means the probe is already known, so a sweep is waste.
WIDTH_WITH_STRONG_CARD = 1

# The fan-out entry point per category. web and dfir split by bug-class family
# through subagent_fanout; the rest are spawned directly as a solver fleet.
FANOUT_FLAG = {"web": "--web", "dfir": "--dfir", "forensics": "--dfir"}
SOLVER_FLEET = {
    "crypto": ["ctf-crypto-recon", "ctf-crypto-rsa", "ctf-crypto-prng",
               "ctf-crypto-ecc", "ctf-crypto-symmetric"],
    "pwn": ["ctf-pwn-triage", "ctf-pwn-stack", "ctf-pwn-format",
            "ctf-pwn-heap", "ctf-pwn-rop"],
    "rev": ["ctf-rev-triage", "ctf-rev-native", "ctf-rev-managed",
            "ctf-rev-bytecode"],
    "osint": ["ctf-osint-image", "ctf-osint-identity", "ctf-osint-infra"],
    "misc": ["ctf-misc-jail", "ctf-misc-encoding"],
}


def agent_cap(cpus=None):
    """The harness's own concurrency cap: min(16, cpus - 2)."""
    cpus = cpus if cpus is not None else (os.cpu_count() or 4)
    return max(1, min(16, cpus - 2))


def width_for(entry, strength):
    """How many agents this one challenge should get, and why."""
    category = entry.get("category") or "unknown"
    grade = (entry.get("chain_match") or "none")
    if isinstance(grade, dict):
        grade = grade.get("status") or "none"

    if grade == "candidate":
        return WIDTH_WITH_STRONG_CARD, (
            "a chain card is a strong match, so run that card's own probe "
            "first; a sweep here would pay spawn latency to rediscover a known "
            "answer")

    info = (strength or {}).get(category) or {}
    fleet = info.get("specialised_agents") or 0
    if fleet <= 1:
        return MIN_USEFUL_WIDTH, (
            "no specialised fleet covers %s, so the generic layer sweep at the "
            "minimum useful width" % category)
    return max(MIN_USEFUL_WIDTH, min(MAX_USEFUL_WIDTH, fleet)), (
        "%d specialised agents exist for %s, capped at %d because ten is a "
        "sweep rather than a wave" % (fleet, category, MAX_USEFUL_WIDTH))


def commands_for(entry, width):
    """The real commands that start this challenge, or a stated gap."""
    category = entry.get("category") or "unknown"
    cid = entry["id"]
    out = []
    flag = FANOUT_FLAG.get(category)
    if flag:
        out.append("python3 tools/subagent_fanout.py %s <handout> --challenge %s"
                   % (flag, cid))
        out.append("# then spawn the briefs it prints IN ONE message so they run "
                   "concurrently")
        out.append("# method: skills/%s-parallel-sweep/SKILL.md"
                   % ("web" if category == "web" else "dfir"))
        return out
    fleet = SOLVER_FLEET.get(category)
    if fleet:
        out.append("# spawn IN ONE message, %d of them: %s"
                   % (min(width, len(fleet)), ", ".join(fleet[:width])))
        out.append("# these are SOLVERS: they may chain to a flag themselves and "
                   "return it with its verbatim excerpt")
        out.append("# a returned flag is a CANDIDATE until this thread runs: "
                   "python3 tools/hooks.py pre-flag %s --value '<flag>' "
                   "--source live-response|artifact --evidence '<excerpt>'" % cid)
        return out
    out.append("python3 tools/subagent_fanout.py --brief <handout> --challenge %s"
               % cid)
    out.append("# no category fleet covers %r; generic layer probers instead"
               % category)
    return out


def plan(ranked, strength, cpus=None, slots=None):
    cap = agent_cap(cpus)
    attack = [e for e in ranked if e.get("action") == "attack_now"]
    if slots is not None:
        attack = attack[:max(0, int(slots))]

    planned, used = [], 0
    for entry in attack:
        width, why = width_for(entry, strength)
        if used + width > cap:
            remaining = cap - used
            if remaining < MIN_USEFUL_WIDTH:
                planned.append({
                    "id": entry["id"], "name": entry.get("name"),
                    "category": entry.get("category"),
                    "width": 0, "action": "hold",
                    "why": "the agent cap of %d is already committed; starting "
                           "this now would only queue it, and a queued agent is "
                           "serial time in a parallel costume" % cap,
                    "commands": [],
                })
                continue
            width = remaining
            why += ("; narrowed to %d by the harness agent cap of %d"
                    % (width, cap))
        used += width
        planned.append({
            "id": entry["id"], "name": entry.get("name"),
            "category": entry.get("category"),
            "expected_minutes": entry.get("expected_minutes"),
            "width": width, "action": "start", "why": why,
            "commands": commands_for(entry, width),
        })

    return {
        "agent_cap": cap,
        "agents_committed": used,
        "headroom": max(0, cap - used),
        "challenges_started": sum(1 for p in planned if p["action"] == "start"),
        "plan": planned,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Plan how many challenges to run at once and how wide each")
    ap.add_argument("event")
    ap.add_argument("--minutes-left", type=float)
    ap.add_argument("--parallel-slots", type=int, default=3,
                    help="how many challenges to start. Default 3: the cap is "
                         "min(16, cpus-2) agents, and the main thread still has "
                         "to drive a spine rather than sit and wait")
    args = ap.parse_args(argv)

    here = str(ROOT / "tools" / "contest")
    if here not in sys.path:
        sys.path.insert(0, here)
    import board as board_mod
    import triage as triage_mod

    try:
        data = board_mod.load(args.event)
    except ValueError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}, ensure_ascii=False))
        return 2

    strength = triage_mod.category_strength()
    ranked = triage_mod.rank(data, strength, args.minutes_left,
                             args.parallel_slots)
    payload = plan(ranked, strength, slots=args.parallel_slots)
    payload["mode"] = "contest-dispatch"
    payload["event"] = data.get("event")
    payload["never"] = [
        "do not let a subagent run tools/hooks.py or tools/state.py: this "
        "thread is the only writer, and ten parallel writers would spend the "
        "probe budget in one round",
        "do not spawn and then wait; drive a spine here while they work",
    ]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
