#!/usr/bin/env python3
"""Build a small SQLite FTS index from reviewed CTF cards."""
import argparse
import glob
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cards", default=os.path.join(ROOT, "knowledge", "cards"))
    ap.add_argument("--db", default=os.path.join(ROOT, "knowledge", "ctf.sqlite3"))
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.db), exist_ok=True)
    db = sqlite3.connect(args.db)
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS cards USING fts5(id, name, event, category, technique, signals, first_probe, source_url)")
    db.execute("DELETE FROM cards")
    accepted = 0
    for filename in glob.glob(os.path.join(args.cards, "**", "*.json"), recursive=True):
        try:
            card = json.load(open(filename, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if card.get("quality", {}).get("review_status") != "reviewed":
            continue
        challenge = card.get("challenge", {})
        classification = card.get("classification", {})
        source = card.get("source", {})
        probe = card.get("first_probe") or {}
        db.execute("INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
            card.get("id", ""), challenge.get("name", ""), challenge.get("event", ""),
            challenge.get("category", ""), classification.get("primary", ""),
            " ".join(card.get("signals", [])), json.dumps(probe, ensure_ascii=False), source.get("url", "")))
        accepted += 1
    db.commit()
    db.close()
    print(json.dumps({"database": args.db, "indexed": accepted}))


if __name__ == "__main__":
    main()
