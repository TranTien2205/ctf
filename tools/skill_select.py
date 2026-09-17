#!/usr/bin/env python3
"""Select exactly one router and at most one depth skill from skills/registry.json.

This is the single dispatcher. It never invents a skill: every id and path it
prints is read from the registry, and a path that is missing on disk is reported
as an error instead of being returned as a suggestion.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ctf import observation_route, source_route  # noqa: E402

REGISTRY = os.path.join(ROOT, "skills", "registry.json")
# ctf.py routes SSRF as its own pseudo-category; the registry stores it under web.
CATEGORY_ALIAS = {"web-ssrf": "web"}


def load_registry(path=REGISTRY):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def by_id(registry):
    return {skill["id"]: skill for skill in registry["skills"]}


def exists(skill):
    return os.path.isfile(os.path.join(ROOT, skill["path"]))


def collect_text(target, limit=400000):
    """Read a bounded amount of source text so unlock signals can be matched."""
    if os.path.isfile(target):
        paths = [target]
    else:
        paths = []
        skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
        for base, dirs, names in os.walk(target):
            dirs[:] = [d for d in dirs if d not in skip]
            paths.extend(os.path.join(base, name) for name in names)
    chunks = []
    total = 0
    for path in paths:
        try:
            if os.path.getsize(path) > 1024 * 1024:
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                data = handle.read(40000)
        except OSError:
            continue
        chunks.append(path + "\n" + data)
        total += len(data)
        if total >= limit:
            break
    return "\n".join(chunks)


def select(text, category, registry, source_mode=False):
    index = by_id(registry)
    problems = []
    chosen_router = None
    for skill in registry["skills"]:
        if skill["layer"] != "router":
            continue
        if category in skill["categories"]:
            chosen_router = skill
            break

    entry = index.get("ctf-playbook")
    open_now = []
    if entry and exists(entry):
        open_now.append({"layer": "entry", "id": entry["id"], "path": entry["path"],
                         "tokens": entry["skill_tokens"]})
    unclassified = False
    if chosen_router is None:
        if category in ("unknown", None, ""):
            unclassified = True
        else:
            problems.append("no router declares category %r" % category)
    elif not exists(chosen_router):
        problems.append("registry path missing on disk: " + chosen_router["path"])
    else:
        open_now.append({"layer": "router", "id": chosen_router["id"],
                         "path": chosen_router["path"], "tokens": chosen_router["skill_tokens"],
                         "use_when": chosen_router["use_when"],
                         "do_not_use_when": chosen_router["do_not_use_when"]})

    unlocked, locked = [], []
    allowed = set(chosen_router["routes_to"]) if chosen_router else set()
    for skill_id in sorted(allowed):
        skill = index.get(skill_id)
        if skill is None:
            problems.append("router routes_to unknown id: " + skill_id)
            continue
        if not exists(skill):
            problems.append("registry path missing on disk: " + skill["path"])
            continue
        if skill["layer"] != "depth":
            continue
        pattern = skill.get("unlock_signals")
        hits = sorted(set(re.findall(pattern, text, re.I)))[:6] if pattern else []
        entry_out = {"id": skill["id"], "path": skill["path"],
                     "tokens": skill["skill_tokens"], "depth_tokens": skill["depth_tokens"],
                     "matched_signals": hits}
        if skill.get("manual_gate"):
            entry_out["manual_gate"] = skill["manual_gate"]
            locked.append(entry_out)
        elif hits:
            unlocked.append(entry_out)
        else:
            entry_out["reason"] = "no unlock signal observed yet"
            locked.append(entry_out)
    unlocked.sort(key=lambda item: (-len(item["matched_signals"]), item["id"]))

    budget = sum(item["tokens"] for item in open_now)
    top = unlocked[0] if unlocked else None
    if top:
        budget += top["tokens"]
    if unclassified:
        step = ("category not established from this input; open ctf-playbook only, "
                "collect one more observation, then re-run this tool")
    elif source_mode:
        step = "read the source end to end, then run one discriminating probe"
    else:
        step = "run the router's cheapest discriminating probe before opening any depth skill"
    return {
        "mode": "skill-select",
        "category": category,
        "classified": not unclassified,
        "open_now": open_now,
        "depth_candidate": top,
        "depth_alternates": unlocked[1:3],
        "locked": locked,
        "next_action": step,
        "estimated_open_tokens": budget,
        "policy": registry["load_policy"]["max_open_at_once"],
        "problems": problems,
    }


def main():
    parser = argparse.ArgumentParser(description="Pick one router and one depth skill")
    parser.add_argument("observation", nargs="?", help="observed text, banner, or challenge description")
    parser.add_argument("--source", help="path to challenge source for white-box selection")
    parser.add_argument("--category", help="force a category instead of routing")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.observation and not args.source:
        parser.error("provide an observation or --source")

    if args.source:
        if not os.path.exists(args.source):
            print(json.dumps({"mode": "skill-select", "error": "source path does not exist",
                              "path": args.source}), file=sys.stderr)
            return 2
        text = collect_text(args.source)
        routed = source_route(args.source)
        counts = {}
        for finding in routed["findings"]:
            counts[finding["category"]] = counts.get(finding["category"], 0) + 1
        category = args.category or (max(counts, key=counts.get) if counts else "unknown")
        source_mode = True
    else:
        text = args.observation
        routed = observation_route(text)
        raw = (routed.get("route") or {}).get("category")
        category = args.category or CATEGORY_ALIAS.get(raw, raw) or "unknown"
        source_mode = False

    registry = load_registry()
    result = select(text, category, registry, source_mode)
    result["input"] = {"kind": "source" if args.source else "observation",
                       "value": args.source or args.observation}
    print(json.dumps(result, ensure_ascii=False) if args.json
          else json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
