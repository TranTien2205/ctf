#!/usr/bin/env python3
"""Return compact reviewed CTF cards from the local SQLite FTS index."""
import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ctf import fts_query


def main():
    ap = argparse.ArgumentParser(description="Query reviewed CTF technique cards")
    ap.add_argument("query")
    ap.add_argument("--category")
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--db", default=os.path.join(ROOT, "knowledge", "ctf.sqlite3"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    sql = "SELECT id, name, event, category, technique, signals, first_probe, source_url FROM cards WHERE cards MATCH ?"
    params = [fts_query(args.query)]
    if args.category:
        sql += " AND category = ?"
        params.append(args.category)
    sql += " LIMIT ?"
    params.append(max(1, min(args.n, 100)))
    db = None
    try:
        db = sqlite3.connect(Path(args.db).resolve().as_uri() + "?mode=ro", uri=True)
        rows = [dict(zip(("id", "name", "event", "category", "technique", "signals", "first_probe", "source_url"), row))
                for row in db.execute(sql, params)] if params[0] else []
    except sqlite3.Error as exc:
        print(json.dumps({"query": args.query, "results": [], "error": str(exc)}))
        return 1
    finally:
        if db is not None:
            db.close()
    print(json.dumps({"query": args.query, "results": rows}, ensure_ascii=False) if args.json else
          "\n".join("[%s] %s / %s — %s" % (row["category"], row["name"], row["technique"], row["source_url"]) for row in rows))


if __name__ == "__main__":
    sys.exit(main())
