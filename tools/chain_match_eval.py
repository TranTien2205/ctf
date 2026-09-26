#!/usr/bin/env python3
"""Measure whether chain_match actually retrieves the right card.

Ground truth comes for free: a chain card names the challenge it was derived
from, and that challenge's handout source is on disk. Feeding the source back in
must rank that card first. Anything else is a retrieval failure, not a solving
failure.

The eval also reports two numbers that predict what happens as the library
grows, which is the question that matters before importing anything:

  signal promiscuity - how many DIFFERENT challenges a single signal literal
      appears in. A signal present in most sources contributes nothing but
      false candidates, and its cost grows with every card added.

  rivals - how many wrong cards score at or above the correct one. This is the
      quantity that scales: if the library grows k-fold with the same signal
      quality, expect roughly k times as many rivals.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chain_match

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHALLENGES = os.path.join(ROOT, "challenges")
# these are this toolkit's own working directories, not handout source; they
# contain solve.py and would leak the answer straight into the query
WORKDIR_MARKERS = ("solve.py", "state.json")


def is_workdir(path):
    try:
        names = set(os.listdir(path))
    except OSError:
        return True
    return any(m in names for m in WORKDIR_MARKERS)


ALIASES = os.path.join(ROOT, "test", "baselines", "chain_match_aliases.json")


def load_aliases():
    """Explicit name -> directory pairings, each one reviewed and measured.

    A card whose challenge name is not its directory name is invisible to the
    eval, which understates retrieval quality. Guessing the pairing by fuzzy
    match would let a wrong pair move top1 without anyone noticing, so the
    pairings live in a file that records, per alias, how many of the card's
    signals were found in that source and where the card ranked there.
    """
    try:
        with open(ALIASES, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, ValueError):
        return {}
    out = {}
    for name, entry in (payload.get("aliases") or {}).items():
        key = name.lower().replace(" ", "").replace("_", "").replace("-", "")
        out[key] = entry.get("directory")
    return out


def source_dir_for(name, aliases=None):
    """Pick the handout directory for a challenge name, ignoring workdirs."""
    if not name:
        return None
    key = name.lower().replace(" ", "").replace("_", "").replace("-", "")
    if aliases is None:
        aliases = load_aliases()
    target = aliases.get(key)
    if target:
        path = os.path.join(CHALLENGES, target)
        if os.path.isdir(path) and not is_workdir(path):
            return path
    best, best_size = None, -1
    for entry in os.listdir(CHALLENGES):
        path = os.path.join(CHALLENGES, entry)
        if not os.path.isdir(path) or is_workdir(path):
            continue
        if entry.lower().replace(" ", "").replace("_", "").replace("-", "") != key:
            continue
        size = sum(len(files) for _, _, files in os.walk(path))
        if size > best_size:
            best, best_size = path, size
    return best


def word_boundary_found(signal, text):
    """Substring containment makes short signals match inside other words.

    chain_match uses `signal.lower() in text`, so `erb` fires on "verbose",
    `id` on "width", `all` on "install" and `cn` on "cnt". Anchoring a signal
    that begins and ends with a word character to word boundaries keeps the
    signal's information while removing those accidental hits.
    """
    import re as _re
    s = signal.lower()
    if s and (s[0].isalnum() or s[0] == "_") and (s[-1].isalnum() or s[-1] == "_"):
        return _re.search(r"\b" + _re.escape(s) + r"\b", text) is not None
    return s in text


def boundary_scorer(sources, base):
    def score(card, text, lowered):
        sigs = card.get("signals", [])
        if not sigs:
            return None
        kept = [s for s in sigs if word_boundary_found(s, lowered)]
        if not kept:
            return None
        shim = dict(card)
        shim["signals"] = sigs
        fake = "\n".join(kept)
        return base(shim, fake, fake)
    return score


def idf_scorer(sources):
    """Weight a matched signal by how rare it is across known challenges.

    The shipped score is matched/len(signals), which hands a card with three
    vague signals a near-perfect ratio on every source while a card with fifteen
    precise ones is penalised for the five that happen not to appear. Weighting
    by rarity removes both effects without discarding any signal by hand.
    """
    import math
    total = max(1, len(sources))

    def df(sig):
        return sum(1 for t in sources.values() if sig.lower() in t)

    cache = {}

    def score(card, text, lowered):
        sigs = card.get("signals", [])
        if not sigs:
            return None
        matched = [s for s in sigs if s.lower() in lowered]
        if not matched:
            return None
        weight = 0.0
        for s in matched:
            if s not in cache:
                cache[s] = math.log((total + 1.0) / (df(s) + 1.0))
            weight += cache[s]
        return {"id": card["id"], "match_confidence": round(weight, 4),
                "signal_coverage": round(len(matched) / len(sigs), 3)}

    return score


def rank_cards(cards, text, scorer=None, stats=None):
    """Rank exactly the way the shipped tool does, including its stats file."""
    lowered = text.lower()
    scored = []
    for card in cards:
        if "_error" in card:
            continue
        if scorer:
            result = scorer(card, text, lowered)
        else:
            result = chain_match.score_card(card, text, lowered, stats)
        if result:
            scored.append(result)
    scored.sort(key=lambda r: (-(r.get("match_weight") or 0.0),
                               -r["match_confidence"],
                               -r.get("signal_coverage", 0.0), r["id"]))
    return scored


def main():
    ap = argparse.ArgumentParser(description="Retrieval quality of chain_match")
    ap.add_argument("--chains", default=chain_match.CHAINS)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--scorer", choices=["shipped", "idf", "boundary", "idf-boundary"],
                    default="shipped")
    ap.add_argument("--drop-promiscuous", type=float, default=None,
                    metavar="FRAC",
                    help="ignore signals that appear in at least FRAC of the "
                         "ground-truth sources; tests whether retrieval quality "
                         "is limited by library SIZE or by signal SPECIFICITY")
    ap.add_argument("--no-stats", action="store_true",
                    help="ignore knowledge/signal-stats.json, i.e. measure the "
                         "pre-rarity behaviour")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    cards = chain_match.load_chains(a.chains)
    cases, per_signal_hits, sources = [], {}, {}
    # challenge NAMES are what source_dir_for resolves, so two cards whose names
    # normalise the same way both claim one handout directory. At most one can be
    # right, which makes the pair untestable rather than failing -- scoring it
    # anyway invented a rank-19 that was the sole source of every rival reported.
    claimed, ambiguous = {}, []

    # first pass: read every ground-truth source so promiscuity can be measured
    # before it is used to filter
    for card in cards:
        if "_error" in card:
            continue
        path = source_dir_for((card.get("challenge") or {}).get("name"))
        if path:
            sources[card["id"]] = chain_match.read_source(path).lower()
            claimed.setdefault(path, []).append(card["id"])

    if a.drop_promiscuous is not None:
        total = max(1, len(sources))
        for card in cards:
            if "_error" in card:
                continue
            kept = [s for s in card.get("signals", [])
                    if sum(1 for t in sources.values() if s.lower() in t) / total
                    < a.drop_promiscuous]
            card["signals"] = kept

    stats = None if a.no_stats else chain_match.load_signal_stats()
    if a.scorer == "idf":
        scorer = idf_scorer(sources)
    elif a.scorer == "boundary":
        scorer = boundary_scorer(sources, chain_match.score_card)
    elif a.scorer == "idf-boundary":
        scorer = boundary_scorer(sources, idf_scorer(sources))
    else:
        scorer = None

    for card in cards:
        if "_error" in card:
            continue
        name = (card.get("challenge") or {}).get("name")
        path = source_dir_for(name)
        if not path:
            continue
        if len(claimed.get(path, [])) > 1:
            rel = os.path.relpath(path, ROOT)
            if any(a["source"] == rel for a in ambiguous):
                continue                      # one entry per directory, not per card
            ambiguous.append({
                "source": os.path.relpath(path, ROOT),
                "claimed_by": sorted(claimed[path]),
                "why": "two challenge names normalise to this one directory, so the "
                       "pairing is a guess; give the losing card its own handout "
                       "directory, or rename one challenge, before trusting a rank here",
            })
            continue
        text = chain_match.read_source(path)
        sources[card["id"]] = text.lower()
        ranked = rank_cards(cards, text, scorer, stats)
        ids = [r["id"] for r in ranked]
        if card["id"] not in ids:
            cases.append({"card": card["id"], "source": os.path.relpath(path, ROOT),
                          "rank": None, "rivals": len(ids), "above": ids[:3]})
            continue
        pos = ids.index(card["id"])
        cases.append({
            "card": card["id"],
            "source": os.path.relpath(path, ROOT),
            "rank": pos + 1,
            "rivals": pos,
            "above": ids[:pos][:3],
            "confidence": ranked[pos]["match_confidence"],
        })

    # signal promiscuity across the ground-truth corpus
    for card in cards:
        if "_error" in card:
            continue
        for sig in card.get("signals", []):
            hits = sum(1 for t in sources.values() if sig.lower() in t)
            key = (card["id"], sig)
            per_signal_hits[key] = hits

    n = len(cases)
    top1 = sum(1 for c in cases if c["rank"] == 1)
    found = [c for c in cases if c["rank"]]
    mrr = sum(1.0 / c["rank"] for c in found) / n if n else 0.0
    rivals = sum(c["rivals"] for c in cases)
    total_sources = max(1, len(sources))
    promiscuous = sorted(
        ((h / total_sources, cid, sig) for (cid, sig), h in per_signal_hits.items()
         if h / total_sources >= 0.5),
        reverse=True)

    report = {
        "cards_total": sum(1 for c in cards if "_error" not in c),
        "cards_with_ground_truth": n,
        "cards_skipped_ambiguous_source": len({a["source"] for a in ambiguous}),
        "ambiguous_sources": ambiguous,
        "top1": top1,
        "top1_rate": round(top1 / n, 3) if n else 0.0,
        "mrr": round(mrr, 3),
        "not_retrieved": sum(1 for c in cases if c["rank"] is None),
        "rivals_total": rivals,
        "rivals_per_query": round(rivals / n, 2) if n else 0.0,
        "promiscuous_signals": len(promiscuous),
        "promiscuous_examples": [
            {"signal": s, "in_fraction_of_sources": round(f, 2), "card": c}
            for f, c, s in promiscuous[:12]],
        "worst_cases": sorted(
            [c for c in cases if c["rank"] != 1],
            key=lambda c: (c["rank"] is not None, c["rank"] or 99), reverse=True)[:8],
    }
    if a.json or not a.verbose:
        print(json.dumps(report, indent=2))
        return 0
    for c in sorted(cases, key=lambda c: c["rank"] or 99):
        print("rank=%-5s rivals=%-3d %s" % (c["rank"], c["rivals"], c["card"][:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
