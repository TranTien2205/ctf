#!/usr/bin/env python3
"""Rank a contest board by points per expected minute, and say what to do now.

The question this answers: twenty challenges, one clock, which do I attack, in
parallel, and which do I drop. Nothing in this tree answered it before; the
only guidance was prose in skills/ctf-playbook/SKILL.md.

Every term in the estimate is MEASURED, not guessed:

* `AGENT_ROUNDTRIP_MINUTES` is 9, from ORCHESTRATION.md's own table -- the
  measured spawn-to-report times there are 9.7, 10.2, 7.3 and 10.2 minutes, and
  the file states 7-10 minutes is "a floor, not a budget", the same whatever the
  task. This single number is why blind fan-out is not free: ten agents on an
  easy challenge costs more than solving it directly, because the time-box for
  an easy challenge is 15-30 minutes (ctf-playbook SKILL.md).

* Category strength is read off disk at runtime by `category_strength()`: how
  many taxonomy classes in that category are `verified` (a chain card proves
  the class was solved here), how many chain cards back them, and how many
  specialised subagents cover the category. It is therefore self-updating: when
  the crypto fleet grew from one agent to five, crypto's estimate improved
  without anyone editing a constant.

* A strong chain-card match is the single best predictor of a fast solve,
  because the card hands back a probe already proven in this tree. It is
  computed offline from the handout and costs no request, which is why
  `tools/chain_match.py` is the cheapest thing on the board.

* Solve count, when the platform publishes it, is the field's own difficulty
  measurement. HTB does not publish it, so `solves: None` means unknown and is
  treated as unknown rather than as zero -- treating it as zero would rank
  every HTB challenge as maximally hard, which is backwards.

This module decides nothing about bug classes and writes no state. It ranks.
"""
import argparse
import json
import os
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ORCHESTRATION.md, measured: spawn-to-report is 7-10 minutes whatever the task.
AGENT_ROUNDTRIP_MINUTES = 9.0

# How many waves a category is expected to need before a flag falls. A wave is
# one parallel fan-out, so its wall-clock cost is roughly one agent round-trip
# regardless of width -- width buys coverage, not time.
WAVES_WITH_STRONG_CARD = 1.0
WAVES_WITH_FLEET = 2.0
WAVES_WITHOUT_FLEET = 4.0

# A card that chain_match graded `candidate` (its `strong` test passed) versus
# one it graded `weak`. holdout_eval measures cross-challenge transfer at
# roughly 0.04, so a weak grade is deliberately given little credit here.
RECALL_FACTOR = {"candidate": 0.35, "weak": 0.85, "none": 1.0}



def category_strength(root=None):
    """Measured, per category: verified classes, backing cards, fleet size.

    Read from disk so the number tracks the tree instead of a stale constant.
    """
    root = Path(root or ROOT)
    out = {}

    # Each taxonomy class carries its own `category` field, so read that rather
    # than parsing the id prefix: `file-read-primitives` is a web class whose id
    # has no `web-` prefix at all, and prefix-guessing silently dropped it.
    verified_by_cat, cards_by_cat = {}, {}
    taxonomy = root / "knowledge" / "bug-classes.json"
    try:
        with open(taxonomy, encoding="utf-8") as handle:
            data = json.load(handle)
        classes = data.get("classes") if isinstance(data, dict) else data
        for entry in classes or []:
            if entry.get("evidence_level") != "verified":
                continue
            cat = (entry.get("category") or "unknown").lower()
            verified_by_cat[cat] = verified_by_cat.get(cat, 0) + 1
            cards_by_cat[cat] = (cards_by_cat.get(cat, 0)
                                 + len(entry.get("verified_by") or []))
    except (OSError, ValueError):
        pass

    agents = root / ".claude" / "agents"
    fleet = {}
    try:
        for path in agents.glob("ctf-*.md"):
            stem = path.stem[len("ctf-"):]
            head = stem.split("-")[0]
            fleet[head] = fleet.get(head, 0) + 1
    except OSError:
        pass
    # The generic scouts are not a category fleet; they serve every category.
    for generic in ("recon", "killmap", "layer", "writeup"):
        fleet.pop(generic, None)

    for category in ("web", "crypto", "pwn", "rev", "forensics", "dfir",
                     "osint", "misc", "ai", "web3", "unknown"):
        # forensics and dfir share both the taxonomy classes and the fleet:
        # tools/subagent_fanout.py --dfir is what covers a forensics bundle.
        key = "dfir" if category in ("dfir", "forensics") else category
        out[category] = {
            "verified_classes": verified_by_cat.get(key, 0),
            "chain_cards": cards_by_cat.get(key, 0),
            "specialised_agents": fleet.get(key, 0),
        }
    return out


def expected_minutes(row, strength):
    """Wall-clock this challenge is expected to cost, and why.

    Returns (minutes, reasons). Reasons are returned so a ranking can be argued
    with rather than trusted: a number with no stated basis is the thing this
    repository's own rules forbid.
    """
    reasons = []
    category = row.get("category") or "unknown"
    info = strength.get(category) or {"verified_classes": 0, "chain_cards": 0,
                                      "specialised_agents": 0}

    grade = ((row.get("chain_match") or {}).get("status") or "none").lower()
    if grade not in RECALL_FACTOR:
        grade = "none"

    if grade == "candidate":
        waves = WAVES_WITH_STRONG_CARD
        reasons.append("a chain card is a strong match, so the first probe is "
                       "already proven here")
    elif info["specialised_agents"] >= 2:
        waves = WAVES_WITH_FLEET
        reasons.append("%d specialised agents cover %s, so one wave measures "
                       "the whole surface at once"
                       % (info["specialised_agents"], category))
    else:
        waves = WAVES_WITHOUT_FLEET
        reasons.append("no specialised fleet covers %s here, so expect serial "
                       "work" % category)

    minutes = AGENT_ROUNDTRIP_MINUTES * waves
    minutes *= RECALL_FACTOR[grade]
    if grade == "weak":
        reasons.append("the chain match is only a weak grade; measured "
                       "cross-challenge transfer is about 0.04, so it earns "
                       "little credit")

    solves = row.get("solves")
    if solves is None:
        reasons.append("the platform publishes no solve count, so difficulty is "
                       "unknown and is not guessed")
    else:
        # Many solvers means easy, and an easy challenge should be banked early.
        # Clamped so a single outlier cannot dominate the ordering.
        factor = max(0.45, min(1.5, 1.5 - 0.9 * _solve_share(solves, strength)))
        minutes *= factor
        reasons.append("%d solves on the board scales the estimate by %.2f"
                       % (solves, factor))

    if info["verified_classes"]:
        minutes *= 0.9
        reasons.append("%d verified %s classes with %d backing cards"
                       % (info["verified_classes"], category, info["chain_cards"]))

    already = float(row.get("active_minutes") or 0.0)
    if already:
        reasons.append("%.0f active minutes already spent are sunk and are not "
                       "charged again" % already)

    return round(max(2.0, minutes), 1), reasons


def probability_of_solving(row, strength):
    """How likely this toolkit is to land this challenge at all, and why.

    Without this the ranker optimises points-per-minute ASSUMING SUCCESS, which
    is the wrong objective in a contest. Measured on a real board: a 100-point
    challenge with 61 solves ranked eighth while a 500-point crypto with 2
    solves ranked second, because 500/26 beats 100/11. In an eight-hour event
    with three parallel slots that ordering banks the hard maybe and skips the
    near-certain point, which is how a scoreboard is lost.

    The three inputs are the same ones expected_minutes uses, so this adds no
    new guesswork -- only the honest admission that time is not the only axis.
    """
    reasons = []
    grade = ((row.get("chain_match") or {}).get("status") or "none").lower()
    solves = row.get("solves")
    category = row.get("category") or "unknown"
    info = strength.get(category) or {}

    if grade == "candidate":
        base = 0.90
        reasons.append("a chain card is a strong match, so the opening probe is "
                       "already proven here")
    elif solves is None:
        # HTB and similar publish no solve count. Neutral, not pessimistic.
        base = 0.50
        reasons.append("no solve count is published, so difficulty is unknown "
                       "and treated as even rather than guessed")
    else:
        share = _solve_share(solves, strength)
        base = max(0.12, min(0.92, 0.12 + 0.80 * share))
        reasons.append("%d solves against a field maximum of %d puts the odds "
                       "near %.0f%%"
                       % (solves,
                          (strength.get("__field__") or {}).get("max_solves") or 0,
                          base * 100))

    # Local capability, measured off disk, not asserted. A category this tree
    # has solved before is one it can solve again; a category with no fleet and
    # no verified class is where the measured contest zero happened.
    if info.get("verified_classes"):
        base = min(0.95, base * 1.15)
        reasons.append("%d verified %s classes back it"
                       % (info["verified_classes"], category))
    if not info.get("specialised_agents"):
        base *= 0.70
        reasons.append("no specialised agent covers %s at all" % category)
    elif info.get("specialised_agents", 0) < 2:
        base *= 0.85
        reasons.append("only one agent covers %s" % category)

    return round(max(0.05, min(0.95, base)), 3), reasons


def _solve_share(solves, strength):
    """Where this solve count sits against the field, in 0..1.

    The field maximum is passed in through `strength["__field__"]` by rank() so
    this stays a pure function of its inputs.
    """
    field_max = (strength.get("__field__") or {}).get("max_solves") or 0
    if not field_max:
        return 0.0
    return max(0.0, min(1.0, float(solves) / float(field_max)))


def rank(board, strength=None, minutes_left=None, parallel_slots=3):
    """Order the board by points per expected minute and assign an action."""
    strength = dict(strength or category_strength())
    rows = [r for r in board.get("challenges", [])]
    solved_counts = [r.get("solves") for r in rows if r.get("solves") is not None]
    strength["__field__"] = {"max_solves": max(solved_counts) if solved_counts else 0}

    scored = []
    for row in rows:
        minutes, reasons = expected_minutes(row, strength)
        probability, odds_why = probability_of_solving(row, strength)
        points = float(row.get("points") or 0)
        status = row.get("status") or "untouched"
        # EXPECTED points per minute: value x the chance of actually banking it,
        # over the time it costs. Ranking on points/minute alone prefers the
        # expensive maybe over the cheap certainty, which is the wrong objective
        # when the clock is the binding constraint.
        score = (points * probability / minutes) if minutes else 0.0
        entry = {"id": row["id"], "name": row.get("name"),
                 "category": row.get("category"), "points": row.get("points"),
                 "solves": row.get("solves"), "status": status,
                 "expected_minutes": minutes,
                 "probability_of_solving": probability,
                 "expected_points": round(points * probability, 1),
                 "score_expected_points_per_minute": round(score, 2),
                 "chain_match": (row.get("chain_match") or {}).get("status", "none"),
                 "why": reasons + odds_why}
        if status in ("solved", "dead"):
            entry["action"] = "done" if status == "solved" else "drop"
            entry["score_expected_points_per_minute"] = 0.0
        else:
            # The clock check happens once, below, after the ordering exists.
            entry["action"] = "queue"
        scored.append(entry)

    live = [e for e in scored if e["action"] == "queue"]
    live.sort(key=lambda e: (-e["score_expected_points_per_minute"], e["expected_minutes"],
                             e["id"]))

    # Anything that cannot fit in the remaining clock is dropped rather than
    # started, because a challenge begun and abandoned costs the whole wave.
    if minutes_left is not None:
        for entry in live:
            if entry["expected_minutes"] > minutes_left:
                entry["action"] = "drop"
                entry["why"] = entry["why"] + [
                    "%.0f expected minutes does not fit the %.0f left on the clock"
                    % (entry["expected_minutes"], minutes_left)]

    # Parked is resolved BEFORE attack_now is handed out, because reviving is a
    # distinct action with its own command (state.py --revive) and a parked
    # challenge that happens to rank first must not be silently restarted as if
    # it were untouched. Getting this order wrong made the top-ranked parked
    # challenge read as attack_now, which loses the parking rationale.
    for entry in scored:
        if entry["status"] == "parked" and entry["action"] == "queue":
            entry["action"] = "revive"
    fits = [e for e in live if e["action"] == "queue"]
    for entry in fits[:max(0, int(parallel_slots))]:
        entry["action"] = "attack_now"

    scored.sort(key=lambda e: (-e["score_expected_points_per_minute"],
                               e["expected_minutes"], e["id"]))
    return scored


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Rank a contest board by points per expected minute")
    ap.add_argument("event")
    ap.add_argument("--minutes-left", type=float,
                    help="minutes remaining in the contest; anything that "
                         "cannot finish inside it is dropped rather than started")
    ap.add_argument("--parallel-slots", type=int, default=3,
                    help="how many challenges to mark attack_now. Default 3: "
                         "the harness caps concurrent agents at min(16, cpus-2) "
                         "and ORCHESTRATION.md warns never to spawn and then "
                         "wait, so the main thread must still drive one spine")
    ap.add_argument("--json", action="store_true", help="machine-readable only")
    args = ap.parse_args(argv)

    here = str(ROOT / "tools" / "contest")
    if here not in sys.path:
        sys.path.insert(0, here)
    import board as board_mod

    try:
        data = board_mod.load(args.event)
    except ValueError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}, ensure_ascii=False))
        return 2

    strength = category_strength()
    ordered = rank(data, strength, args.minutes_left, args.parallel_slots)
    attack = [e for e in ordered if e["action"] == "attack_now"]

    payload = {
        "mode": "contest-triage",
        "event": data.get("event"),
        "challenges": len(ordered),
        "category_strength_measured_from_disk": strength,
        "attack_now": [e["id"] for e in attack],
        "ranked": ordered,
        "note": ("expected_minutes is built from ORCHESTRATION.md's measured "
                 "7-10 minute agent round-trip; a strong chain card is the "
                 "cheapest win on the board and costs no request"),
        "next": ["python3 tools/contest/dispatch.py %s" % args.event],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
