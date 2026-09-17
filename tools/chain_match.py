#!/usr/bin/env python3
"""Match the current observation or source against chains this toolkit already solved.

A match is a candidate hypothesis and its cheapest confirming probe. It is never
proof. The tool reports which signals were actually found, which were not, and
which preconditions a human still has to confirm; it never asserts that a
precondition holds.
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAINS = os.path.join(ROOT, "knowledge", "chains")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
MAX_FILE_BYTES = 1024 * 1024
MAX_PER_FILE = 40000
MAX_TOTAL = 400000


def load_chains(directory=CHAINS):
    cards = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        try:
            with open(path, encoding="utf-8") as handle:
                card = json.load(handle)
        except (OSError, ValueError) as exc:
            cards.append({"_error": str(exc), "_path": path})
            continue
        card["_path"] = os.path.relpath(path, ROOT)
        cards.append(card)
    return cards


def read_source(target):
    if os.path.isfile(target):
        paths = [target]
    else:
        paths = []
        for base, dirs, names in os.walk(target):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            paths.extend(os.path.join(base, name) for name in names)
    chunks, total = [], 0
    for path in paths:
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                data = handle.read(MAX_PER_FILE)
        except OSError:
            continue
        chunks.append(os.path.basename(path) + "\n" + data)
        total += len(data)
        if total >= MAX_TOTAL:
            break
    return "\n".join(chunks)


def found(signal, text):
    """Literal, case-insensitive containment. Signals are literals, not regexes."""
    return signal.lower() in text


def score_card(card, text, lowered):
    signals = card.get("signals", [])
    if not signals:
        return None
    matched = [s for s in signals if found(s, lowered)]
    stack = [s for s in card.get("stack", []) if found(s, lowered)]
    if not matched:
        return None
    ratio = len(matched) / len(signals)
    bonus = min(0.15, 0.05 * len(stack))
    confidence = min(0.95, round(ratio + bonus, 3))
    return {
        "id": card["id"],
        "card": card["_path"],
        "source_note": card.get("source_note"),
        "challenge": card.get("challenge", {}).get("name"),
        "category": card.get("challenge", {}).get("category"),
        "stack_matched": stack,
        "signals_matched": matched,
        "signals_missing": [s for s in signals if s not in matched],
        "signal_coverage": round(ratio, 3),
        "match_confidence": confidence,
        "suggested_priority": max(10, min(90, int(round(confidence * 100)))),
        "status": "candidate",
        "preconditions_to_confirm": card.get("preconditions", {}),
        "first_confirming_probe": card.get("first_confirming_probe"),
        "blast_radius": card.get("blast_radius"),
        "known_traps": card.get("known_traps", []),
        "verification_of_original": card.get("verification", {}),
        "chain_outline": [step["stage"] + ": " + step["action"] for step in card.get("chain", [])],
    }


def main():
    parser = argparse.ArgumentParser(description="Match observations against solved chains")
    parser.add_argument("observation", nargs="?")
    parser.add_argument("--source", help="challenge source path for white-box matching")
    parser.add_argument("-n", type=int, default=3, help="maximum candidates to return")
    parser.add_argument("--min-coverage", type=float, default=0.15,
                        help="minimum fraction of a card's signals that must appear")
    parser.add_argument("--chains", default=CHAINS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.observation and not args.source:
        parser.error("provide an observation or --source")

    if args.source:
        if not os.path.exists(args.source):
            print(json.dumps({"mode": "chain-match", "error": "source path does not exist",
                              "path": args.source}), file=sys.stderr)
            return 2
        text = read_source(args.source)
        kind = "source"
    else:
        text = args.observation
        kind = "observation"
    lowered = text.lower()

    cards = load_chains(args.chains)
    broken = [{"path": c.get("_path"), "error": c["_error"]} for c in cards if "_error" in c]
    scored = []
    for card in cards:
        if "_error" in card:
            continue
        result = score_card(card, text, lowered)
        if result and result["signal_coverage"] >= args.min_coverage:
            scored.append(result)
    scored.sort(key=lambda item: (-item["match_confidence"], item["id"]))
    top = scored[: max(1, args.n)]

    output = {
        "mode": "chain-match",
        "input": {"kind": kind, "value": args.source or args.observation},
        "cards_available": len([c for c in cards if "_error" not in c]),
        "candidates": top,
        "broken_cards": broken,
        "rules": [
            "A candidate is a hypothesis, not proof. Run its first confirming probe before acting on the chain.",
            "Confirm every precondition from your own evidence; this tool does not check them.",
            "On mismatch lower the priority and keep the hypothesis open; do not delete it.",
            "Read blast_radius before any write on a shared instance.",
        ],
    }
    if not top:
        output["next_action"] = "no solved chain matches; proceed from the router's first probe"
    else:
        output["next_action"] = ("run the first_confirming_probe of " + top[0]["id"]
                                 + " and record the exact result")
    print(json.dumps(output, ensure_ascii=False) if args.json
          else json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
