#!/usr/bin/env python3
"""Inventory locally available challenge handouts without copying their contents.

Chain retrieval can only be measured against handouts still present locally. This
tool records which chain cards have a handout, excluding solver workdirs that
contain solve.py or state.json. The optional manifest contains only relative
directory names, file counts and byte totals; raw challenge source remains under
the gitignored challenges/ directory and is never imported into knowledge/.
"""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAINS = ROOT / "knowledge" / "chains"
CHALLENGES = ROOT / "challenges"
OUT = ROOT / "knowledge" / "handout-inventory.json"
WORKDIR_MARKERS = {"solve.py", "state.json"}


def normalized(value):
    return "".join(c for c in (value or "").lower() if c.isalnum())


def is_handout(path):
    try:
        return path.is_dir() and not (WORKDIR_MARKERS & {entry.name for entry in path.iterdir()})
    except OSError:
        return False


def choose_handout(challenge_name):
    key = normalized(challenge_name)
    candidates = [p for p in CHALLENGES.iterdir() if normalized(p.name) == key and is_handout(p)] \
        if CHALLENGES.is_dir() else []
    if not candidates:
        return None
    def size(path):
        return sum(entry.stat().st_size for entry in path.rglob("*") if entry.is_file())
    return max(candidates, key=size)


def inventory():
    cards = []
    for path in sorted(CHAINS.glob("*.json")):
        try:
            card = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        challenge = (card.get("challenge") or {}).get("name")
        handout = choose_handout(challenge)
        row = {"chain_id": card.get("id"), "challenge": challenge,
               "handout_available": handout is not None}
        if handout is not None:
            files = [entry for entry in handout.rglob("*") if entry.is_file()]
            row.update({
                "handout_dir": str(handout.relative_to(ROOT)),
                "file_count": len(files),
                "byte_count": sum(entry.stat().st_size for entry in files),
            })
        cards.append(row)
    available = sum(row["handout_available"] for row in cards)
    return {
        "schema_version": 1,
        "policy": "inventory only; raw handouts remain gitignored and are never copied into knowledge",
        "summary": {"chain_cards": len(cards), "with_handout": available,
                    "without_handout": len(cards) - available,
                    "coverage": round(available / len(cards), 3) if cards else 0.0},
        "cards": cards,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="write the safe inventory manifest to knowledge/")
    args = parser.parse_args()
    result = inventory()
    if args.write:
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["written"] = str(OUT.relative_to(ROOT))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
