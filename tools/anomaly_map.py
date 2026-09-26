#!/usr/bin/env python3
"""Record author-deliberate anomalies and per-chain reachability falsifiers.

A high-value white-box challenge has one authored vulnerability. The author had
to add code to create it, and usually more code to close the cheap unintended
paths. Every such oddity is an anomaly that some hypothesis must explain.

This tool is a ledger, not a judge. It stores what the operator observed and
prints two lists that are easy to ignore when they live only in a head:

  * anomalies with no hypothesis that explains them -- an unexplained anomaly
    means the intended path is elsewhere;
  * candidate chains whose cheapest reachability falsifier has not been run --
    that list is the work that is not allowed to start yet.

It never decides a bug class, never confirms a chain and never writes a verdict;
verdicts and flags belong to tools/hooks.py. Stored anomalies hold a one-line
description plus file:line, so raw challenge source is not copied anywhere.

See skills/white-box-intended-path/SKILL.md.
"""
import argparse
import json
import os
import re
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1

# The oddity shapes an author leaves behind. Free text is allowed via "other";
# the point of the list is to make a shape easier to name than to forget.
KINDS = (
    "added",            # code upstream does not have
    "removed",          # code upstream has and the handout dropped
    "sanitizer",        # a hand-rolled cleaner next to a library that does the job
    "whitelist",        # permits exactly one odd input shape
    "blocked-sibling",  # an explicit block on the sibling of a permitted shape
    "word-filter",      # one literal token filtered out of every string
    "raw-sink",         # triple-stash / |safe / innerHTML, often in an unrelated file
    "leftover-record",  # an author fixture, scratch row, commented payload
    "comment",          # a comment that explains a defence
    "version-pin",      # a pinned or downgraded dependency
    "topology",         # an extra container, internal network, setuid helper
    "other",
)


def path_for(name):
    """Mirror tools/state.py: same id grammar, same symlink refusal."""
    safe = name.lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,99}", safe):
        raise ValueError("challenge ID must be 1-100 ASCII letters/digits/dots/"
                         "underscores/hyphens, starting alphanumeric")
    base = (ROOT / "challenges").resolve()
    path = base / safe / "anomaly_map.json"
    if base.is_symlink() or path.parent.is_symlink() or path.is_symlink():
        raise ValueError("anomaly map path uses a symlink")
    if not path.resolve().is_relative_to(base):
        raise ValueError("anomaly map path escapes challenge storage")
    return path


def atomic_json(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=str(path.parent), delete=False) as handle:
            temporary = handle.name
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, str(path))
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def load(path, name):
    if path.exists():
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    return {"schema_version": SCHEMA_VERSION, "name": name,
            "stock_baseline": None, "anomalies": [], "chains": []}


def short_id():
    return uuid.uuid4().hex[:8]


def find_one(items, wanted, label):
    """Accept a full id or an unambiguous prefix."""
    if not wanted:
        raise KeyError("empty %s id" % label)
    exact = [i for i in items if i["id"] == wanted]
    if exact:
        return exact[0]
    prefixed = [i for i in items if i["id"].startswith(wanted)]
    if len(prefixed) == 1:
        return prefixed[0]
    if not prefixed:
        raise KeyError("no %s with id %r" % (label, wanted))
    raise KeyError("%r matches %d entries of kind %s: %s"
                   % (wanted, len(prefixed), label,
                      ", ".join(i["id"] for i in prefixed)))


def unexplained(state):
    return [a for a in state["anomalies"] if not a.get("explained_by")]


def falsifier_not_run(state):
    return [c for c in state["chains"] if not c.get("falsifier_run")]


def no_falsifier_stated(state):
    return [c for c in state["chains"] if not c.get("falsifier")]


def report(state, path):
    open_anoms = unexplained(state)
    pending = falsifier_not_run(state)
    missing = no_falsifier_stated(state)
    out = {
        "mode": "anomaly-map",
        "path": str(path.relative_to(ROOT)),
        "challenge": state["name"],
        "stock_baseline": state.get("stock_baseline"),
        "counts": {
            "anomalies": len(state["anomalies"]),
            "unexplained": len(open_anoms),
            "chains": len(state["chains"]),
            "chains_without_falsifier_stated": len(missing),
            "chains_with_falsifier_not_run": len(pending),
        },
        "unexplained_anomalies": [
            {k: a.get(k) for k in ("id", "kind", "where", "anomaly")} for a in open_anoms
        ],
        "chains_blocked_until_falsifier_runs": [
            {k: c.get(k) for k in ("id", "chain", "falsifier", "cost_minutes")}
            for c in pending
        ],
        "rules": [
            "An unexplained anomaly means the intended path is elsewhere: stop digging where you are.",
            "Never start a chain whose reachability falsifier has not been run.",
            "A falsifier must be read-only; if the cheapest observation writes, use the cheapest read instead.",
            "This tool records observations only. Verdicts and flags go through tools/hooks.py.",
        ],
    }
    if missing:
        out["next_action"] = ("state a reachability falsifier for chain(s) "
                             + ", ".join(c["id"] for c in missing)
                             + " before working them")
    elif pending:
        cheapest = sorted(pending, key=lambda c: (c.get("cost_minutes") is None,
                                                  c.get("cost_minutes") or 0))[0]
        out["next_action"] = ("run the falsifier of %s first: %s"
                             % (cheapest["id"], cheapest["falsifier"]))
    elif open_anoms:
        out["next_action"] = ("explain anomaly %s (%s) or change mechanism layer; "
                             "an unexplained anomaly outranks the current chain"
                             % (open_anoms[0]["id"], open_anoms[0]["where"] or "no location"))
    elif not state["anomalies"]:
        out["next_action"] = ("diff the handout against a stock app of this type and record what the "
                             "author ADDED, REMOVED or GUARDED with --add-anomaly")
    else:
        out["next_action"] = ("every anomaly is explained and every falsifier has run; "
                             "run tools/decide.py %s" % state["name"])
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Anomaly map and reachability falsifiers for a white-box challenge")
    ap.add_argument("name", help="challenge id, as used by tools/state.py")
    ap.add_argument("--stock-baseline",
                    help="what the handout was diffed against (image, package, tag)")
    ap.add_argument("--add-anomaly", metavar="TEXT",
                    help="one line: the author-deliberate oddity, no source excerpt")
    ap.add_argument("--where", metavar="FILE:LINE",
                    help="location of the anomaly; must be a real path on disk")
    ap.add_argument("--kind", choices=KINDS, default="other",
                    help="which oddity shape this is (default: other)")
    ap.add_argument("--explain", metavar="ANOMALY_ID",
                    help="attach the hypothesis that explains an anomaly")
    ap.add_argument("--hypothesis", metavar="TEXT",
                    help="the explanation, required with --explain")
    ap.add_argument("--chain", metavar="CHAIN_ID",
                    help="candidate chain the explanation belongs to (optional)")
    ap.add_argument("--unexplain", metavar="ANOMALY_ID",
                    help="withdraw an explanation that did not hold up")
    ap.add_argument("--add-chain", metavar="TEXT", help="register a candidate chain")
    ap.add_argument("--falsifier", metavar="TEXT",
                    help="cheapest read-only observation that would kill the chain")
    ap.add_argument("--cost", metavar="MINUTES", type=float,
                    help="cost of running that observation, in minutes")
    ap.add_argument("--ran", metavar="CHAIN_ID", help="record that a falsifier was run")
    ap.add_argument("--result", metavar="TEXT",
                    help="verbatim output of the falsifier, required with --ran")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--killed", action="store_true",
                       help="the falsifier closed the chain")
    group.add_argument("--survived", action="store_true",
                       help="the chain survived its falsifier and may be worked")
    ap.add_argument("--show", action="store_true", help="print the map and exit")
    args = ap.parse_args()

    try:
        path = path_for(args.name)
    except ValueError as exc:
        print(json.dumps({"mode": "anomaly-map", "error": str(exc)}), file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        state = load(path, args.name.lower())
    except ValueError as exc:
        print(json.dumps({"mode": "anomaly-map", "error": "unreadable map: %s" % exc}),
              file=sys.stderr)
        return 2

    now = time.time()
    changed = False
    events = []

    if args.stock_baseline:
        state["stock_baseline"] = args.stock_baseline
        changed = True
        events.append("stock baseline recorded")

    if args.add_anomaly:
        where = args.where
        # "Every path named must exist on disk" -- refuse a location that does not.
        if where:
            candidate = where.split(":", 1)[0]
            probe = Path(candidate)
            if not probe.is_absolute():
                probe = ROOT / candidate
            if not probe.exists():
                print(json.dumps({"mode": "anomaly-map", "error":
                                  "--where names a path that does not exist on disk",
                                  "path": candidate}), file=sys.stderr)
                return 2
        entry = {"id": short_id(), "kind": args.kind, "where": where,
                 "anomaly": args.add_anomaly, "explained_by": None, "time": now}
        state["anomalies"].append(entry)
        changed = True
        events.append("anomaly %s recorded (unexplained)" % entry["id"])

    if args.explain:
        if not args.hypothesis:
            ap.error("--explain requires --hypothesis")
        try:
            entry = find_one(state["anomalies"], args.explain, "anomaly")
        except KeyError as exc:
            print(json.dumps({"mode": "anomaly-map", "error": exc.args[0]}), file=sys.stderr)
            return 2
        entry["explained_by"] = {"hypothesis": args.hypothesis,
                                 "chain": args.chain, "time": now}
        changed = True
        events.append("anomaly %s explained" % entry["id"])

    if args.unexplain:
        try:
            entry = find_one(state["anomalies"], args.unexplain, "anomaly")
        except KeyError as exc:
            print(json.dumps({"mode": "anomaly-map", "error": exc.args[0]}), file=sys.stderr)
            return 2
        entry["explained_by"] = None
        changed = True
        events.append("anomaly %s reopened" % entry["id"])

    if args.add_chain:
        entry = {"id": short_id(), "chain": args.add_chain,
                 "falsifier": args.falsifier, "cost_minutes": args.cost,
                 "falsifier_run": None, "status": "candidate", "time": now}
        state["chains"].append(entry)
        changed = True
        events.append("chain %s registered%s"
                      % (entry["id"], "" if args.falsifier else
                         " WITHOUT a falsifier -- state one before working it"))

    if args.ran:
        if not args.result:
            ap.error("--ran requires --result (the verbatim output)")
        try:
            entry = find_one(state["chains"], args.ran, "chain")
        except KeyError as exc:
            print(json.dumps({"mode": "anomaly-map", "error": exc.args[0]}), file=sys.stderr)
            return 2
        if args.falsifier and not entry.get("falsifier"):
            entry["falsifier"] = args.falsifier
        if not entry.get("falsifier"):
            print(json.dumps({"mode": "anomaly-map", "error":
                              "chain has no falsifier stated; pass --falsifier with --ran",
                              "chain": entry["id"]}), file=sys.stderr)
            return 2
        entry["falsifier_run"] = {"result": args.result, "time": now}
        if args.killed:
            entry["status"] = "killed"
        elif args.survived:
            entry["status"] = "survived"
        else:
            entry["status"] = "inconclusive"
        changed = True
        events.append("chain %s falsifier run -> %s" % (entry["id"], entry["status"]))

    if changed:
        atomic_json(path, state)

    out = report(state, path)
    if events:
        out["events"] = events
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
