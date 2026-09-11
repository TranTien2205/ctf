#!/usr/bin/env python3
"""Validate once, then publish a reviewed card without replacing existing data."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

try:
    from .validate_card import validate
except ImportError:
    from validate_card import validate

ROOT = Path(__file__).resolve().parents[1]


def promote(card, critic, dest):
    if not isinstance(critic, dict) or critic.get("accept") is not True or critic.get("errors"):
        raise ValueError("critic rejected card")
    errors = validate(card)
    if errors:
        raise ValueError("; ".join(errors))
    dest = Path(dest).resolve()
    if not dest.is_relative_to(ROOT.resolve()):
        raise ValueError("destination must be inside the toolkit")
    destination = dest / (card["id"] + ".json")
    if destination.parent != dest:
        raise ValueError("unsafe destination")
    card["quality"]["review_status"] = "reviewed"
    dest.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=dest, delete=False) as handle:
            temporary = handle.name
            json.dump(card, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        # Linking publishes complete bytes atomically and fails if the name exists.
        os.link(temporary, destination)
    finally:
        if temporary:
            os.unlink(temporary)
    return str(destination)


def main():
    ap = argparse.ArgumentParser(description="Promote reviewed CTF card (no overwrite)")
    ap.add_argument("card")
    ap.add_argument("critic")
    ap.add_argument("--dest", default=str(ROOT / "knowledge/cards"))
    args = ap.parse_args()
    try:
        with open(args.card, encoding="utf-8") as handle:
            card = json.load(handle)
        with open(args.critic, encoding="utf-8") as handle:
            critic = json.load(handle)
        destination = promote(card, critic, args.dest)
    except (OSError, ValueError) as exc:
        print(json.dumps({"promoted": False, "reason": str(exc)}))
        return 1
    print(json.dumps({"promoted": True, "destination": destination}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
