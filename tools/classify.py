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
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY = os.path.join(ROOT, "knowledge", "bug-classes.json")
WRITEUP_CARDS = os.path.join(ROOT, "knowledge", "cards")
MISSES = os.path.join(ROOT, "knowledge", "classify-misses.log")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
             "vendor", "site-packages"}
MAX_FILE_BYTES = 2 * 1024 * 1024
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz",
              ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".so", ".pyc", ".class", ".jar"}
# A verified class has been solved here; a catalogue class has not. The bonus
# breaks ties toward what this toolkit can actually back up with a chain card.
VERIFIED_BONUS = 0.5
SIGNAL_STATS = os.path.join(ROOT, "knowledge", "classify-signal-stats.json")
# Scratch this toolkit writes into a challenge directory. Counting it would make
# a signal look common because we kept writing about it.
WORKDIR_NAMES = {"solve.py", "state.json", "anomaly_map.json", "notes.md"}


def load_signal_stats(path=SIGNAL_STATS):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    return data if isinstance(data.get("df"), dict) else None


SIGNAL_FLOOR = 0.4   # what a matched signal is worth however common it is


def signal_weight(class_id, signal, stats):
    """A matched signal is worth between SIGNAL_FLOOR and 1.0 by how rare it is.

    The score used to be a plain count, so every matched signal was worth one.
    Measured over the 40 handouts on disk, thirteen of the taxonomy's 174 signals
    match more than 60% of them: web-file-upload's matches 95%, and
    web-auth-session's `alg\\b|hs256|rs256|none` matches 88% because `none` hits
    every Python `None`. Under a count those outvoted a precise signal.

    Rarity modulates the count here rather than replacing it. Replacing it was
    tried first and was worse: summing raw log-rarity made web-cache-poisoning
    lose the EncoDecept observation to web-parser-differential, because two
    corroborating signals at 68% each summed to less than one signal at 55%.
    Two independent signals firing is real evidence even when each is common, so
    breadth discounts a signal toward the floor instead of erasing it.
    """
    if not stats:
        return 1.0
    total = max(1, int(stats.get("corpus", 1)))
    df = int(stats.get("df", {}).get("%s||%s" % (class_id, signal), 0))
    rarity = math.log((total + 1.0) / (df + 1.0)) / math.log(total + 1.0)
    return SIGNAL_FLOOR + (1.0 - SIGNAL_FLOOR) * max(0.0, min(1.0, rarity))


def load_taxonomy(path=TAXONOMY):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _normalise_class_label(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


WRITEUP_CLASS_ALIASES = {
    "sql-injection": "web-sqli",
    "sqli": "web-sqli",
    "nosql-injection": "web-nosqli",
    "command-injection": "web-command-injection",
    "server-side-template-injection": "web-ssti",
    "cross-site-scripting": "web-xss",
    "cross-site-request-forgery": "web-csrf",
}


def load_writeup_signals(directory=WRITEUP_CARDS, classes=None):
    """Load only reviewed writeup signal literals, grouped by primary class.

    Writeups are external claims. They may suggest recognition vocabulary only;
    their probes, verdicts, confidence, and verification never enter the local
    taxonomy or controller.
    """
    signals = {}
    if not os.path.isdir(directory):
        return signals
    for path in sorted(os.path.join(directory, name) for name in os.listdir(directory)
                       if name.endswith(".json")):
        try:
            with open(path, encoding="utf-8") as handle:
                card = json.load(handle)
        except (OSError, ValueError):
            continue
        quality = card.get("quality") or {}
        if quality.get("review_status") != "reviewed":
            continue
        label = (card.get("classification") or {}).get("primary")
        if not label or not isinstance(card.get("signals"), list):
            continue
        if classes is None:
            class_id = label
        else:
            aliases = {}
            for entry in classes:
                aliases[_normalise_class_label(entry["id"])] = entry["id"]
                aliases[_normalise_class_label(entry["name"])] = entry["id"]
                aliases[_normalise_class_label(entry["id"].removeprefix("web-"))] = entry["id"]
            normalized_label = _normalise_class_label(label)
            class_id = aliases.get(normalized_label) or WRITEUP_CLASS_ALIASES.get(normalized_label)
            if class_id is None:
                continue
        signals.setdefault(class_id, []).extend(
            item.strip() for item in card["signals"]
            if isinstance(item, str) and item.strip())
    return {class_id: sorted(set(items)) for class_id, items in signals.items()}


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


def merge_writeup_signals(classes, writeup_signals):
    """Add reviewed writeup signals as literal regexes; keep taxonomy policy authoritative."""
    merged = []
    for entry in classes:
        clone = dict(entry)
        if writeup_signals.get(entry["id"]):
            source_patterns = list(entry.get("source_signals", []))
            observation_patterns = list(entry.get("observation_signals", []))
            # Escape external strings so they are exact literals, never patterns.
            reviewed = [re.escape(s) for s in writeup_signals[entry["id"]]]
            clone["source_signals"] = source_patterns + reviewed
            clone["observation_signals"] = observation_patterns + reviewed
        merged.append(clone)
    return merged


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


def rank(hits, classes, stats=None):
    index = {entry["id"]: entry for entry in classes}
    ranked = []
    for class_id, evidence in hits.items():
        entry = index[class_id]
        matched = {item["signal"] for item in evidence}
        distinct = len(matched)
        total = len(entry.get("observation_signals", [])) + len(entry.get("source_signals", []))
        # Coverage breaks ties: a class whose whole signature fired fits better than
        # one where a few generic signals did.
        coverage = round(distinct / total, 3) if total else 0.0
        weight = sum(signal_weight(class_id, signal, stats) for signal in matched)
        score = weight + (VERIFIED_BONUS if entry["evidence_level"] == "verified" else 0.0)
        ranked.append({
            "class": class_id,
            "name": entry["name"],
            "evidence_level": entry["evidence_level"],
            "verified_by": entry["verified_by"],
            "score": round(score, 2),
            "scoring": "signal-rarity" if stats else "signal-count",
            "match_weight": round(weight, 4),
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


def rebuild_stats(taxonomy_path=TAXONOMY):
    """Count, for every taxonomy signal, how many handouts its pattern matches.

    The same corpus rule chain_match.py uses: a challenge directory counts when
    it holds at least three files that are not this toolkit's own scratch.
    """
    base = os.path.join(ROOT, "challenges")
    corpus = []
    for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        path = os.path.join(base, name)
        if not os.path.isdir(path):
            continue
        real = 0
        for _, _, files in os.walk(path):
            real += sum(1 for f in files if f not in WORKDIR_NAMES)
        if real < 3:
            continue
        chunks, total = [], 0
        for item in walk_source(path):
            if os.path.basename(item) in WORKDIR_NAMES:
                continue
            try:
                if os.path.getsize(item) > MAX_FILE_BYTES:
                    continue
                with open(item, encoding="utf-8", errors="replace") as handle:
                    chunks.append(handle.read(40000))
            except OSError:
                continue
            total += len(chunks[-1])
            if total >= 400000:
                break
        corpus.append("\n".join(chunks).lower())

    classes = load_taxonomy(taxonomy_path)["classes"]
    df = {}
    for entry in classes:
        signals = (entry.get("observation_signals", [])
                   + entry.get("source_signals", []))
        for signal in signals:
            try:
                pattern = re.compile(signal, re.I)
            except re.error:
                continue
            df["%s||%s" % (entry["id"], signal)] = sum(
                1 for text in corpus if pattern.search(text))
    data = {"corpus": len(corpus), "signals": len(df), "df": df}
    with open(SIGNAL_STATS, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    broad = sum(1 for v in df.values() if corpus and v / len(corpus) > 0.6)
    print(json.dumps({"written": os.path.relpath(SIGNAL_STATS, ROOT),
                      "corpus": data["corpus"], "signals": data["signals"],
                      "signals_matching_over_60pct": broad}, indent=2))
    return 0


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
    parser.add_argument("--rebuild-stats", action="store_true",
                        help="recount how many handouts each taxonomy signal matches "
                             "and write knowledge/classify-signal-stats.json, then exit")
    args = parser.parse_args()

    if args.rebuild_stats:
        return rebuild_stats(args.taxonomy)

    observation = " ".join(args.observation).strip()
    if not observation and not args.source:
        parser.error("provide an observation or --source")

    taxonomy = load_taxonomy(args.taxonomy)
    classes = merge_writeup_signals(
        taxonomy["classes"], load_writeup_signals(classes=taxonomy["classes"]))
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

    stats = load_signal_stats()
    ranked = [item for item in rank(hits, classes, stats)
              if item["signals_matched"] >= args.min_signals]
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
