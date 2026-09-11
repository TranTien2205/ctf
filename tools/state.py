#!/usr/bin/env python3
"""Create/update a compact per-challenge state file."""
import argparse
import json
import os
import time
import re
import tempfile
import uuid
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path_for(name):
    safe = name.lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,99}", safe):
        raise ValueError("challenge ID must be 1-100 ASCII letters/digits/dots/underscores/hyphens, starting alphanumeric")
    base = Path(ROOT).resolve() / "challenges"
    path = base / safe / "state.json"
    if base.is_symlink() or path.parent.is_symlink() or path.is_symlink() or not path.resolve().is_relative_to(base):
        raise ValueError("state path escapes challenge storage or uses a symlink")
    return str(path)


def atomic_json(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=os.path.dirname(path), delete=False) as handle:
            temporary = handle.name
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def main():
    ap = argparse.ArgumentParser(description="Manage CTF challenge state")
    ap.add_argument("name")
    ap.add_argument("--category")
    ap.add_argument("--target")
    ap.add_argument("--hypothesis")
    ap.add_argument("--probe")
    ap.add_argument("--result")
    ap.add_argument("--next")
    ap.add_argument("--close", help="close the selected hypothesis with this reason")
    ap.add_argument("--hypothesis-id", help="select hypothesis for a probe or lifecycle update")
    ap.add_argument("--status", choices=("open", "confirmed", "rejected", "closed"))
    ap.add_argument("--decision", help="record an agent decision")
    ap.add_argument("--priority", type=int, choices=range(0, 101),
                    help="set selected hypothesis priority from 0 to 100")
    ap.add_argument("--deprioritize", help="keep selected hypothesis open at priority 0")
    args = ap.parse_args()
    try:
        path = path_for(args.name)
    except ValueError as exc:
        ap.error(str(exc))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, encoding="utf-8") as handle:
            state = json.load(handle)
    except FileNotFoundError:
        state = {"schema_version": 1, "name": args.name, "category": args.category,
                  "target": args.target, "hypotheses": [], "probes": [], "next_action": None}
    except (OSError, ValueError) as exc:
        ap.error("state not changed: " + str(exc))
    if not isinstance(state, dict) or any(not isinstance(state.get(key), list) for key in ("hypotheses", "probes")) or any(not isinstance(h, dict) for h in state["hypotheses"]):
        ap.error("invalid state structure; state not changed")
    if "decisions" in state and not isinstance(state["decisions"], list):
        ap.error("invalid decisions; state not changed")
    for hypothesis in state["hypotheses"]:
        hypothesis.setdefault("id", uuid.uuid4().hex)
    selected = None
    if args.hypothesis_id:
        matches = [h for h in state["hypotheses"] if h["id"] == args.hypothesis_id]
        if len(matches) != 1:
            ap.error("hypothesis ID must identify exactly one existing hypothesis")
        selected = matches[0]
    if (args.close or args.status) and selected is None:
        ap.error("--close/--status requires --hypothesis-id")
    if args.close and args.status:
        ap.error("choose --close or --status")
    if args.category:
        state["category"] = args.category
    if args.target:
        state["target"] = args.target
    if args.hypothesis:
        state["hypotheses"].append({"id": uuid.uuid4().hex, "name": args.hypothesis,
                                    "status": "open", "priority": 50, "time": time.time()})
    if args.probe:
        state["probes"].append({"request": args.probe, "result": args.result or "unknown", "time": time.time()})
        if selected is not None:
            state["probes"][-1]["hypothesis_id"] = selected["id"]
    if args.next:
        state["next_action"] = args.next
    if args.close or args.status:
        selected.setdefault("history", []).append({"status": selected.get("status"), "reason": selected.get("reason"), "time": time.time()})
        selected["status"] = "closed" if args.close else args.status
        selected["reason"] = args.close
    if args.priority is not None or args.deprioritize:
        if selected is None:
            ap.error("--priority/--deprioritize requires --hypothesis-id")
        selected["priority"] = 0 if args.deprioritize else args.priority
        if args.deprioritize:
            selected["deprioritized_reason"] = args.deprioritize
    if args.decision:
        state.setdefault("decisions", []).append({"text": args.decision, "time": time.time()})
    state["updated_at"] = time.time()
    atomic_json(path, state)
    print(json.dumps({"path": path, "state": state}, ensure_ascii=False))


if __name__ == "__main__":
    main()
