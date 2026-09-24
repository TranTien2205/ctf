#!/usr/bin/env python3
"""Match the current observation or source against chains this toolkit already solved.

A match is a candidate hypothesis and its cheapest confirming probe. It is never
proof. The tool reports which signals were actually found, which were not, and
which preconditions a human still has to confirm; it never asserts that a
precondition holds.
"""
import argparse
import glob
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAINS = os.path.join(ROOT, "knowledge", "chains")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
SIGNAL_STATS = os.path.join(ROOT, "knowledge", "signal-stats.json")
MAX_FILE_BYTES = 1024 * 1024
MAX_PER_FILE = 40000
MAX_TOTAL = 400000


def load_chains(directory=CHAINS):
    cards = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        try:
            with open(path, encoding="utf-8") as handle:
                card = json.load(handle)
        except (OSError, ValueError) as exc:
            cards.append({"_error": str(exc), "_path": path})
            continue
        card["_path"] = os.path.relpath(path, ROOT)
        cards.append(card)
    return cards


# Assets carry no signals but happily consume the whole read budget. An
# asset-heavy challenge used to spend all 400 KB on a sourcemap and a few JPEGs,
# so the matcher never saw its own Dockerfile or handler code and the card could
# not be retrieved from its own handout at all.
SKIP_EXT = {
    ".jpg", ".jpeg", ".png", ".gif", ".ico", ".bmp", ".webp", ".svg",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".zip", ".gz", ".tgz", ".xz", ".bz2", ".7z", ".rar",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".webm",
    ".so", ".dll", ".dylib", ".class", ".jar", ".wasm", ".pyc",
    ".map", ".lock", ".ttc", ".db", ".sqlite", ".sqlite3", ".pack", ".idx",
}
SKIP_NAME_PARTS = (".min.js", ".min.css", "package-lock.json", "yarn.lock",
                   "pnpm-lock.yaml", "go.sum", "composer.lock", "Gemfile.lock")
# read the files most likely to define the challenge first
PRIORITY_EXT = (".vcl", ".conf", ".cfg", ".ini", ".toml", ".env",
                ".go", ".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".rb",
                ".php", ".java", ".rs", ".zig", ".c", ".cpp", ".sh", ".sql",
                ".json", ".yml", ".yaml", ".html", ".txt", ".md")


def _worth_reading(path):
    name = os.path.basename(path)
    if any(part in name for part in SKIP_NAME_PARTS):
        return False
    return os.path.splitext(name)[1].lower() not in SKIP_EXT


def _read_order(path):
    """Dockerfiles and entrypoints first, then source, then everything else."""
    name = os.path.basename(path).lower()
    ext = os.path.splitext(name)[1].lower()
    if name.startswith("dockerfile") or name in ("entrypoint.sh", "docker-compose.yml",
                                                 "supervisord.conf"):
        rank = 0
    elif ext in PRIORITY_EXT:
        rank = 1 + PRIORITY_EXT.index(ext)
    else:
        rank = len(PRIORITY_EXT) + 2
    try:
        size = os.path.getsize(path)
    except OSError:
        size = MAX_FILE_BYTES
    return (rank, size)


def read_source(target):
    if os.path.isfile(target):
        paths = [target]
    else:
        paths = []
        for base, dirs, names in os.walk(target):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            paths.extend(os.path.join(base, name) for name in names)
        paths = sorted((p for p in paths if _worth_reading(p)), key=_read_order)
    chunks, total = [], 0
    for path in paths:
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                data = handle.read(MAX_PER_FILE)
        except OSError:
            continue
        chunks.append(os.path.basename(path) + "\n" + data)
        total += len(data)
        if total >= MAX_TOTAL:
            break
    return "\n".join(chunks)


def found(signal, text):
    """Literal, case-insensitive containment. Signals are literals, not regexes."""
    return signal.lower() in text


def load_signal_stats(path=SIGNAL_STATS):
    """Document frequency of each signal across the handout corpus.

    Scoring a match by how RARE its signal is fixes a bias that grows with the
    library: the old score was matched/len(signals), which handed a card with
    three vague signals a near-perfect ratio on every source while a card with
    fifteen precise ones was penalised for the five that happened not to appear.
    Measured over the cards whose handout is still on disk, the old score put the
    right card first 73% of the time with 1.91 wrong cards outranking it; this
    one scores 91% with 0.55. Rebuild with --rebuild-stats.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or "corpus" not in data:
        return None
    return data


def signal_weight(signal, stats):
    """Rarer signals count for more. Unknown signals are treated as rare."""
    total = max(1, int(stats.get("corpus", 1)))
    df = int(stats.get("df", {}).get(signal, 0))
    return math.log((total + 1.0) / (df + 1.0))


def score_card(card, text, lowered, stats=None):
    signals = card.get("signals", [])
    if not signals:
        return None
    matched = [s for s in signals if found(s, lowered)]
    stack = [s for s in card.get("stack", []) if found(s, lowered)]
    if not matched:
        return None
    ratio = len(matched) / len(signals)
    if stats:
        # rank on the raw summed rarity. An earlier attempt squashed it with
        # 1-exp(-weight) so the reported number would stay inside 0..1, but that
        # saturates above about weight 3, every strong card reported 0.95 and the
        # real ordering was decided by card id. Keep the weight for ranking and
        # derive a bounded number only for display.
        weight = sum(signal_weight(s, stats) for s in matched)
        confidence = min(0.95, round(weight / (weight + 3.0), 3))
    else:
        weight = None
        bonus = min(0.15, 0.05 * len(stack))
        confidence = min(0.95, round(ratio + bonus, 3))
    return {
        "id": card["id"],
        "match_weight": None if weight is None else round(weight, 4),
        "card": card["_path"],
        "source_note": card.get("source_note"),
        "challenge": card.get("challenge", {}).get("name"),
        "category": card.get("challenge", {}).get("category"),
        "stack_matched": stack,
        "signals_matched": matched,
        "signals_missing": [s for s in signals if s not in matched],
        "signal_coverage": round(ratio, 3),
        "match_confidence": confidence,
        "suggested_priority": max(10, min(90, int(round(confidence * 100)))),
        "status": "candidate",
        "preconditions_to_confirm": card.get("preconditions", {}),
        "first_confirming_probe": card.get("first_confirming_probe"),
        "blast_radius": card.get("blast_radius"),
        "known_traps": card.get("known_traps", []),
        "verification_of_original": card.get("verification", {}),
        "chain_outline": [step["stage"] + ": " + step["action"] for step in card.get("chain", [])],
    }


def rebuild_stats(chains_dir):
    """Count, for every signal any card names, how many handouts contain it."""
    workdir_markers = ("solve.py", "state.json")
    corpus = []
    base = os.path.join(ROOT, "challenges")
    for entry in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        path = os.path.join(base, entry)
        if not os.path.isdir(path):
            continue
        try:
            names = set(os.listdir(path))
        except OSError:
            continue
        if any(m in names for m in workdir_markers):
            continue          # this toolkit's own scratch dir, not a handout
        if sum(len(files) for _, _, files in os.walk(path)) < 3:
            continue
        corpus.append(read_source(path).lower())

    signals = set()
    for card in load_chains(chains_dir):
        if "_error" not in card:
            signals.update(card.get("signals", []))
    df = {s: sum(1 for t in corpus if s.lower() in t) for s in sorted(signals)}
    data = {"corpus": len(corpus), "signals": len(df), "df": df}
    with open(SIGNAL_STATS, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"written": os.path.relpath(SIGNAL_STATS, ROOT),
                      "corpus": data["corpus"], "signals": data["signals"]}, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Match observations against solved chains")
    parser.add_argument("observation", nargs="?")
    parser.add_argument("--source", help="challenge source path for white-box matching")
    parser.add_argument("-n", type=int, default=3, help="maximum candidates to return")
    parser.add_argument("--min-coverage", type=float, default=0.15,
                        help="minimum fraction of a card's signals that must appear")
    parser.add_argument("--chains", default=CHAINS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--rebuild-stats", action="store_true",
                        help="recount signal frequencies over challenges/ and write "
                             "knowledge/signal-stats.json, then exit")
    args = parser.parse_args()

    if args.rebuild_stats:
        return rebuild_stats(args.chains)
    if not args.observation and not args.source:
        parser.error("provide an observation or --source")

    if args.source:
        if not os.path.exists(args.source):
            print(json.dumps({"mode": "chain-match", "error": "source path does not exist",
                              "path": args.source}), file=sys.stderr)
            return 2
        text = read_source(args.source)
        kind = "source"
    else:
        text = args.observation
        kind = "observation"
    lowered = text.lower()

    cards = load_chains(args.chains)
    stats = load_signal_stats()
    broken = [{"path": c.get("_path"), "error": c["_error"]} for c in cards if "_error" in c]
    scored = []
    for card in cards:
        if "_error" in card:
            continue
        result = score_card(card, text, lowered, stats)
        if result and result["signal_coverage"] >= args.min_coverage:
            scored.append(result)
    scored.sort(key=lambda item: (-(item.get("match_weight") or 0.0),
                                  -item["match_confidence"], item["id"]))
    top = scored[: max(1, args.n)]

    output = {
        "mode": "chain-match",
        "input": {"kind": kind, "value": args.source or args.observation},
        "cards_available": len([c for c in cards if "_error" not in c]),
        "scoring": "signal-rarity" if stats else "signal-ratio",
        "candidates": top,
        "broken_cards": broken,
        "rules": [
            "A candidate is a hypothesis, not proof. Run its first confirming probe before acting on the chain.",
            "Confirm every precondition from your own evidence; this tool does not check them.",
            "On mismatch lower the priority and keep the hypothesis open; do not delete it.",
            "Read blast_radius before any write on a shared instance.",
        ],
    }
    if not top:
        output["next_action"] = "no solved chain matches; proceed from the router's first probe"
    else:
        output["next_action"] = ("run the first_confirming_probe of " + top[0]["id"]
                                 + " and record the exact result")
    print(json.dumps(output, ensure_ascii=False) if args.json
          else json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
