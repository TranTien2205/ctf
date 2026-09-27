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
# A new hypothesis starts mid-scale so an explicit raise or a park is visible.
DEFAULT_PRIORITY = 50
# A revived branch comes back below a fresh one until new evidence raises it.
REVIVE_PRIORITY = 40


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
    ap.add_argument("--source",
                    help="path to the supplied handout, so a resumed session and "
                         "tools/decide.py can both find the source again")
    ap.add_argument("--challenge-name",
                    help="the challenge's real name, for the writeup-search rule")
    ap.add_argument("--event", help="the event it came from, for the writeup-search rule")
    ap.add_argument("--hypothesis")
    ap.add_argument("--bug-class", help="taxonomy class owned by the hypothesis")
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
    ap.add_argument("--revive", help="reopen a parked or closed hypothesis with this reason")
    ap.add_argument("--show", action="store_true",
                    help="print the hypothesis ledger by priority and change nothing")
    args = ap.parse_args()
    try:
        path = path_for(args.name)
    except ValueError as exc:
        ap.error(str(exc))
    # A read must not mint storage. --show used to create the directory before it
    # was consulted, so a mistyped or wrongly-cased name left an empty challenge
    # dir behind; those dirs then outnumbered real handouts in challenges/.
    if not args.show:
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
    if "searches" in state and not isinstance(state["searches"], list):
        ap.error("invalid searches; state not changed")
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
    if args.revive and selected is None:
        ap.error("--revive requires --hypothesis-id")
    if args.revive and (args.close or args.deprioritize):
        ap.error("--revive cannot be combined with --close or --deprioritize")
    if args.show:
        ledger = sorted(state["hypotheses"], key=lambda h: (-(h.get("priority") or 0), h.get("time", 0)))
        # bug_class is what the control loop keys on, and category/target/source
        # are what decide.py reads to pick its next action, so a --show that
        # hides them makes the documented resume (--show then decide.py) a guess.
        print(json.dumps({"path": path, "name": state.get("name"),
                          "category": state.get("category"),
                          "target": state.get("target"),
                          "source": state.get("source"),
                          "next_action": state.get("next_action"),
                          "hypotheses": [{"id": h["id"], "name": h.get("name"),
                                          "bug_class": h.get("bug_class"),
                                          "status": h.get("status"),
                                          "priority": h.get("priority"),
                                          "reason": h.get("reason") or h.get("deprioritized_reason")}
                                         for h in ledger]}, ensure_ascii=False))
        return
    if args.category:
        state["category"] = args.category
    if args.target:
        state["target"] = args.target
    # tools/decide.py rule 8 offers a writeup search once either is known. Nothing
    # could write them, so that rule never fired and the shortcut both CLAUDE.md
    # and AGENTS.md call legitimate was unreachable from the controller.
    # A resumed session used to get a target URL and a hypothesis list with no
    # path to the source it had been reasoning about, and decide.py could not
    # name the novel-plan command because it did not know where the handout was.
    if args.source:
        state["source"] = args.source
    if args.challenge_name:
        state["challenge_name"] = args.challenge_name
    if args.event:
        state["event_name"] = args.event
    if args.hypothesis:
        created = {"id": uuid.uuid4().hex, "name": args.hypothesis,
                   "bug_class": args.bug_class, "status": "open",
                   "priority": DEFAULT_PRIORITY, "time": time.time()}
        state["hypotheses"].append(created)
        if selected is None:
            selected = created
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
    if args.revive:
        selected.setdefault("history", []).append({"status": selected.get("status"),
                                                   "reason": selected.get("reason"),
                                                   "priority": selected.get("priority"),
                                                   "time": time.time()})
        selected["status"] = "open"
        selected["priority"] = REVIVE_PRIORITY if args.priority is None else args.priority
        selected["revived_reason"] = args.revive
        selected.pop("deprioritized_reason", None)
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
