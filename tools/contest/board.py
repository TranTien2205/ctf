#!/usr/bin/env python3
"""The contest-level board: many challenges, one clock, one ranked queue.

Why this exists. Every executable thing in this tree was scoped to ONE
challenge. `tools/state.py` stores `challenges/<name>/state.json` and
`tools/decide.py` takes a single name and reasons over a single ledger; neither
has any notion that another challenge exists. Measured on disk: 130 challenge
directories, no index, nothing that walks them. So "I have twenty challenges
and eight hours, which do I attack first" was answered only by prose in
`skills/ctf-playbook/SKILL.md`, never by a tool.

That matters for speed more than anything inside a single challenge, because of
a measured asymmetry: the budgets in `tools/decide.py` bite WITHIN one
challenge's ledger and there is no shared state between challenges at all.
Running many different challenges at once trips no shared budget. Parallelism
across challenges is free; parallelism inside one is what the brake governs.

This module is a SIBLING PLANE, built the way `tools/ad/` is: it does not
import the jeopardy controller's internals, it never writes
`challenges/<name>/state.json`, and it never records a verdict or a flag.
`tools/hooks.py` remains the only write gate for those. This file ranks work
and nothing else.
"""
import argparse
import csv
import json
import os
import re
import time
from pathlib import Path

# parents[2] from tools/contest/board.py is the repository root, and resolve()
# first so a symlinked checkout still lands inside the tree rather than beside it.
ROOT = Path(__file__).resolve().parents[2]

STATUSES = ("untouched", "running", "parked", "solved", "dead")
CATEGORIES = ("web", "crypto", "pwn", "rev", "forensics", "dfir",
              "osint", "misc", "ai", "web3", "unknown")


def board_path(event):
    """contests/<event>/board.json, with the same guards state.py uses.

    The slug rule and the symlink/traversal check are lifted from
    tools/state.py:path_for because they are already correct there: a read must
    not mint storage and a name must not escape its directory.
    """
    safe = event.lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,99}", safe):
        raise ValueError(
            "event ID must be 1-100 ASCII letters/digits/dots/underscores/"
            "hyphens, starting alphanumeric")
    base = ROOT / "contests"
    path = base / safe / "board.json"
    if (base.is_symlink() or path.parent.is_symlink() or path.is_symlink()
            or (path.exists() and not path.resolve().is_relative_to(base.resolve()))):
        raise ValueError("board path escapes contest storage or uses a symlink")
    return path


def atomic_json(path, data):
    """tempfile + fsync + os.replace, the same shape as tools/state.py.

    A board is written while agents are running against it, so a half-written
    file is a real risk rather than a theoretical one.
    """
    import tempfile
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=os.path.dirname(path),
                                         delete=False) as handle:
            temporary = handle.name
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def empty_board(event, ends_at=None):
    return {"schema_version": 1, "event": event, "ends_at": ends_at,
            "challenges": []}


def normalise(entry):
    """One challenge row, with every field the ranker needs present.

    `solves` is None rather than 0 when the platform does not publish it: HTB
    does not, and treating "unknown" as "nobody solved it" would rank every HTB
    challenge as maximally hard, which is the opposite of true.
    """
    name = entry.get("name") or entry.get("id")
    if not name:
        raise ValueError("a challenge row needs at least a name or an id")
    challenge_id = entry.get("id") or re.sub(r"[^a-z0-9._-]+", "-", name.lower()).strip("-")
    category = (entry.get("category") or "unknown").lower()
    if category not in CATEGORIES:
        category = "unknown"
    status = entry.get("status") or "untouched"
    if status not in STATUSES:
        raise ValueError("status must be one of %s" % ", ".join(STATUSES))
    solves = entry.get("solves")
    if solves is not None:
        solves = int(solves)
    return {
        "id": challenge_id,
        "name": name,
        "category": category,
        "points": int(entry.get("points") or 0),
        "solves": solves,
        "status": status,
        "challenge_dir": entry.get("challenge_dir"),
        "source": entry.get("source"),
        "target": entry.get("target"),
        "fanout_width": int(entry.get("fanout_width") or 0),
        "active_minutes": float(entry.get("active_minutes") or 0.0),
        "probes": int(entry.get("probes") or 0),
        "flag": entry.get("flag"),
        "chain_match": entry.get("chain_match") or {"status": "none",
                                                    "card": None,
                                                    "confidence": 0.0},
        "notes": entry.get("notes"),
    }


def load(event):
    path = board_path(event)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return empty_board(event)
    except (OSError, ValueError) as exc:
        raise ValueError("board not readable: %s" % exc)
    if not isinstance(data, dict) or not isinstance(data.get("challenges"), list):
        raise ValueError("invalid board structure; board not changed")
    return data


def save(event, board):
    path = board_path(event)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    atomic_json(path, board)
    return path


# ------------------------------------------------------------------ adapters
# The manual adapter is first on purpose: the ranking core must work before any
# platform is wired in, and a board you can paste is a board you can use at a
# contest whose API you have not reverse engineered yet. A CTFd and an HTB
# adapter are later plugins; each only has to return a list of raw rows.

def rows_from_json(path):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    rows = data.get("challenges") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError("expected a list of challenges, or {\"challenges\": [...]}")
    return rows


def rows_from_csv(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def ingest(event, rows, replace=False):
    """Merge rows into the board, preserving progress on rows already there.

    A re-ingest during a contest must not wipe the fact that a challenge is
    solved or parked, so an existing row keeps its own status, flag, timings and
    chain_match and only takes fresh points and solve counts from the platform.
    """
    board = load(event)
    existing = {c["id"]: c for c in board["challenges"]}
    out = [] if replace else list(board["challenges"])
    index = {c["id"]: i for i, c in enumerate(out)}
    added, updated = 0, 0
    for raw in rows:
        fresh = normalise(raw)
        prior = existing.get(fresh["id"])
        if prior and not replace:
            merged = dict(prior)
            merged["points"] = fresh["points"] or prior.get("points") or 0
            if fresh["solves"] is not None:
                merged["solves"] = fresh["solves"]
            for key in ("category", "target", "source", "challenge_dir"):
                if fresh.get(key):
                    merged[key] = fresh[key]
            out[index[fresh["id"]]] = merged
            updated += 1
        else:
            out.append(fresh)
            index[fresh["id"]] = len(out) - 1
            added += 1
    board["challenges"] = out
    board["updated_at"] = time.time()
    return board, added, updated


def set_fields(board, challenge_id, **fields):
    for row in board["challenges"]:
        if row["id"] == challenge_id:
            for key, value in fields.items():
                if value is not None:
                    row[key] = value
            return row
    raise ValueError("no challenge with id %r on this board" % challenge_id)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Contest board: ingest, show and update many challenges")
    ap.add_argument("event", help="contest slug; the board lives in contests/<event>/")
    ap.add_argument("--ends-at", help="ISO-8601 end time, e.g. 2026-10-06T18:00:00Z. "
                                     "Typed in, never computed: the workflow "
                                     "sandbox has no clock and bfs rejects "
                                     "relative timestamps on this box")
    ap.add_argument("--ingest-json", help="a JSON file of challenge rows")
    ap.add_argument("--ingest-csv", help="a CSV file of challenge rows")
    ap.add_argument("--replace", action="store_true",
                    help="replace the roster instead of merging into it")
    ap.add_argument("--id", help="select one challenge for an update")
    ap.add_argument("--status", choices=STATUSES)
    ap.add_argument("--flag", help="record a flag STRING on the board for "
                                   "scoreboard bookkeeping; this is NOT the "
                                   "proof gate. A flag only counts once "
                                   "tools/hooks.py pre-flag has accepted it")
    ap.add_argument("--challenge-dir")
    ap.add_argument("--source")
    ap.add_argument("--target")
    ap.add_argument("--fanout-width", type=int)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args(argv)

    try:
        if args.show:
            board = load(args.event)
            print(json.dumps({"mode": "contest-board", "event": board["event"],
                              "ends_at": board.get("ends_at"),
                              "challenges": len(board["challenges"]),
                              "by_status": _counts(board),
                              "rows": board["challenges"]},
                             ensure_ascii=False, indent=2))
            return 0

        board = load(args.event)
        added = updated = 0
        rows = []
        if args.ingest_json:
            rows += rows_from_json(args.ingest_json)
        if args.ingest_csv:
            rows += rows_from_csv(args.ingest_csv)
        if rows:
            board, added, updated = ingest(args.event, rows, replace=args.replace)
        if args.ends_at:
            board["ends_at"] = args.ends_at
        if args.id:
            set_fields(board, args.id, status=args.status, flag=args.flag,
                       challenge_dir=args.challenge_dir, source=args.source,
                       target=args.target, fanout_width=args.fanout_width)
        path = save(args.event, board)
    except ValueError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}, ensure_ascii=False))
        return 2

    print(json.dumps({"mode": "contest-board", "ok": True,
                      "event": args.event, "board": str(path.relative_to(ROOT)),
                      "added": added, "updated": updated,
                      "challenges": len(board["challenges"]),
                      "by_status": _counts(board),
                      "next": "python3 tools/contest/triage.py %s" % args.event},
                     ensure_ascii=False, indent=2))
    return 0


def _counts(board):
    out = {}
    for row in board["challenges"]:
        out[row.get("status", "untouched")] = out.get(row.get("status", "untouched"), 0) + 1
    return out


if __name__ == "__main__":
    raise SystemExit(main())
