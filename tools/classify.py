#!/usr/bin/env python3
"""Classify a challenge into bug classes from the signals actually observed.

Black-box:  python3 tools/classify.py "<observation text>"
White-box:  python3 tools/classify.py --source ./challenge-src

Every hit carries its evidence: the signal that matched and, for source input,
the exact file and line. A class is a candidate with a first probe and a
falsifier — never a finding. Nothing is invented: the taxonomy lives in
knowledge/bug-classes.json and this tool only matches against it.

An input that matches nothing is appended to knowledge/classify-misses.log.
That log is the backlog of classes this toolkit does not know yet.
"""
import argparse
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY = os.path.join(ROOT, "knowledge", "bug-classes.json")
MISSES = os.path.join(ROOT, "knowledge", "classify-misses.log")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
             "vendor", "site-packages"}
MAX_FILE_BYTES = 2 * 1024 * 1024
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz",
              ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".so", ".pyc", ".class", ".jar"}
# A verified class has been solved here; a catalogue class has not. The bonus
# breaks ties toward what this toolkit can actually back up with a chain card.
VERIFIED_BONUS = 0.5


def load_taxonomy(path=TAXONOMY):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def compile_signals(classes, field):
    compiled = {}
    for entry in classes:
        patterns = []
        for raw in entry.get(field, []):
            try:
                patterns.append((raw, re.compile(raw, re.I)))
            except re.error as exc:
                print("bad regex in %s.%s: %s (%s)" % (entry["id"], field, raw, exc),
                      file=sys.stderr)
        compiled[entry["id"]] = patterns
    return compiled


def walk_source(target):
    if os.path.isfile(target):
        yield target
        return
    for base, dirs, names in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(names):
            if os.path.splitext(name)[1].lower() in BINARY_EXT:
                continue
            yield os.path.join(base, name)


def scan_source(target, compiled, limit_per_class=4):
    """Return {class_id: [{signal, file, line, excerpt}]} with real file positions."""
    hits = {}
    for path in walk_source(target):
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        for class_id, patterns in compiled.items():
            bucket = hits.setdefault(class_id, [])
            # The cap counts DISTINCT signals. Recording the same signal once per
            # file used to exhaust it before the remaining signals were ever
            # tried, so a class scored on how many files matched rather than on
            # how many different signals did.
            seen = {item["signal"] for item in bucket}
            if len(seen) >= limit_per_class:
                continue
            for raw, pattern in patterns:
                if raw in seen:
                    continue
                match = pattern.search(text)
                if not match:
                    continue
                line = text.count("\n", 0, match.start()) + 1
                excerpt = text[match.start():match.start() + 100].splitlines()[0].strip()
                bucket.append({"signal": raw,
                               "file": os.path.relpath(path, os.path.dirname(target.rstrip("/")) or "."),
                               "line": line, "excerpt": excerpt[:100]})
                seen.add(raw)
                if len(seen) >= limit_per_class:
                    break
    return {k: v for k, v in hits.items() if v}


def scan_text(text, compiled, limit_per_class=6):
    hits = {}
    for class_id, patterns in compiled.items():
        bucket = []
        for raw, pattern in patterns:
            match = pattern.search(text)
            if match:
                bucket.append({"signal": raw, "matched": match.group(0)[:60]})
            if len(bucket) >= limit_per_class:
                break
        if bucket:
            hits[class_id] = bucket
    return hits


def rank(hits, classes):
    index = {entry["id"]: entry for entry in classes}
    ranked = []
    for class_id, evidence in hits.items():
        entry = index[class_id]
        distinct = len({item["signal"] for item in evidence})
        total = len(entry.get("observation_signals", [])) + len(entry.get("source_signals", []))
        # Coverage breaks ties: a class whose whole signature fired fits better than
        # one where a few generic signals did.
        coverage = round(distinct / total, 3) if total else 0.0
        score = distinct + (VERIFIED_BONUS if entry["evidence_level"] == "verified" else 0.0)
        ranked.append({
            "class": class_id,
            "name": entry["name"],
            "evidence_level": entry["evidence_level"],
            "verified_by": entry["verified_by"],
            "score": round(score, 2),
            "signals_matched": distinct,
            "signals_defined": total,
            "coverage": coverage,
            "skill": entry["skill"],
            "first_probe": entry["first_probe"],
            "falsifier": entry["falsifier"],
            "blast_radius": entry.get("blast_radius"),
            "confusable_with": entry.get("confusable_with", []),
            "depth_refs": entry.get("depth_refs", []),
            "evidence": evidence,
            "status": "candidate",
        })
    ranked.sort(key=lambda item: (-item["score"], -item["coverage"], item["class"]))
    return ranked


def log_miss(kind, value):
    try:
        line = "%s\t%s\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 kind, re.sub(r"\s+", " ", value)[:300])
        with open(MISSES, "a", encoding="utf-8") as handle:
            handle.write(line)
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description="Classify a challenge into bug classes")
    parser.add_argument("observation", nargs="*", help="observed text, banner, or description")
    parser.add_argument("--source", help="path to challenge source for white-box classification")
    parser.add_argument("-n", type=int, default=5, help="maximum candidates to return")
    parser.add_argument("--min-signals", type=int, default=1,
                        help="drop candidates below this many distinct matched signals")
    parser.add_argument("--only", choices=("verified", "catalogue"),
                        help="restrict to classes at this evidence level")
    parser.add_argument("--taxonomy", default=TAXONOMY)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    observation = " ".join(args.observation).strip()
    if not observation and not args.source:
        parser.error("provide an observation or --source")

    taxonomy = load_taxonomy(args.taxonomy)
    classes = taxonomy["classes"]
    if args.only:
        classes = [c for c in classes if c["evidence_level"] == args.only]

    if args.source:
        if not os.path.exists(args.source):
            print(json.dumps({"mode": "classify", "error": "source path does not exist",
                              "path": args.source}), file=sys.stderr)
            return 2
        hits = scan_source(args.source, compile_signals(classes, "source_signals"))
        if observation:
            for class_id, evidence in scan_text(observation,
                                                compile_signals(classes, "observation_signals")).items():
                hits.setdefault(class_id, []).extend(evidence)
        kind, value = "source", args.source
    else:
        hits = scan_text(observation, compile_signals(classes, "observation_signals"))
        kind, value = "observation", observation

    ranked = [item for item in rank(hits, classes) if item["signals_matched"] >= args.min_signals]
    top = ranked[: max(1, args.n)]
    if not top:
        log_miss(kind, value)

    result = {
        "mode": "classify",
        "input": {"kind": kind, "value": value},
        "classes_considered": len(classes),
        "candidates": top,
        "rules": taxonomy["rules"],
    }
    if top:
        result["next_action"] = ("run the first_probe of %s and record the exact result"
                                 % top[0]["class"])
        if top[0]["evidence_level"] == "catalogue":
            result["caution"] = ("top candidate is a catalogue class: this toolkit has never "
                                 "solved one, so its skill is a starting point, not proven knowledge")
    else:
        result["next_action"] = ("no class matched; the input was appended to "
                                 "knowledge/classify-misses.log as a gap to close")
    print(json.dumps(result, ensure_ascii=False) if args.json
          else json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
