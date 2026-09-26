#!/usr/bin/env python3
"""Does the chain index transfer to a challenge it has never seen?

tools/chain_match_eval.py asks whether card X is retrieved by challenge X. That
is a memory test: a card's signals are literals copied out of that challenge's
own handout, so any substring index scores near 1.0 on it. It catches index rot,
which is worth having, but it cannot answer the question that decides how much a
new card is worth:

    a challenge arrives whose shape nothing here has solved.
    Does the library say anything useful, or does it go quiet?

This holds each card out of the index, then queries with that card's handout —
which is now, from the index's point of view, a novel challenge. Three outcomes:

The headline is `abstained` and `confidence_on_phantom`. Measured over 24
held-out cards: the index abstained 0 times and reported a median confidence of
0.653, up to 0.891, on a card that was not the answer. chain_match turns that
number into suggested_priority, and decide.py rule 6 then runs that card's
first_confirming_probe ahead of the agent's own hypothesis. So on an unseen
challenge the system does not go quiet — it confidently proposes a wrong probe.

`related_rate` is reported too but read it as a floor, not a verdict: it is a
Jaccard over stack and chain wording, and inspection showed it scoring genuine
transfer as unrelated (two JWT key-confusion cards overlapped 0.099, under the
0.12 threshold). Use it to compare runs, not to settle whether cards generalise.
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import chain_match as cm            # noqa: E402
import chain_match_eval as cme      # noqa: E402

WORKDIR_NAMES = {"solve.py", "state.json", "anomaly_map.json", "notes.md"}


FAMILIES = os.path.join(ROOT, "test", "baselines", "mechanism_families.json")


def reviewed_peers():
    """{card: {peer}} from a labelling produced outside this tool.

    Ground truth used to be the card->class filing in skills/*/field-notes.md,
    widened by the taxonomy's confusable_with. That had to go for two reasons.

    The filing is wrong for several cards: classify_card scored the whole card at
    once, so the exploit narrative outvoted the opening move, and a chain opening
    on a recursive merge into an object was filed under SSRF.

    Worse, it leaked. A retrieval approach that keys on the filing then scores
    well for agreeing with the very labels the metric is defined over. The
    winning approach in the 2026-09-26 bake-off disclosed this itself and put its
    leak-free number at 0.083 against the 0.208 it reported.

    What replaces it: three annotators labelled the handout-backed cards blind,
    reading only knowledge/chains/*.json, and a pair is kept only on two-of-three
    agreement. Nothing a retriever can reach is consulted.
    """
    try:
        with open(FAMILIES, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, ValueError):
        return {}
    out = {}
    for entry in doc.get("pairs", []):
        a, b = entry["pair"]
        out.setdefault(a, set()).add(b)
        out.setdefault(b, set()).add(a)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-coverage", type=float, default=0.15,
                        help="same admission floor tools/chain_match.py uses")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cards = [c for c in cm.load_chains() if "_error" not in c]
    stats = cm.load_signal_stats()
    aliases = cme.load_aliases()
    reviewed = reviewed_peers()
    results, measured = [], 0

    for held in cards:
        peers = reviewed.get(held["id"])
        if not peers:
            continue                          # no reviewed peer: nothing could be right
        source = cme.source_dir_for((held.get("challenge") or {}).get("name"), aliases)
        if not source:
            continue
        measured += 1
        text = cm.read_source(source, skip_names=WORKDIR_NAMES)
        lowered = text.lower()
        scored = []
        for other in cards:
            if other["id"] == held["id"]:
                continue                      # the hold-out
            hit = cm.score_card(other, text, lowered, stats)
            if hit and hit["signal_coverage"] >= args.min_coverage:
                scored.append(hit)
        # Count a weak top result as an abstention: that is what chain_match now
        # does with it — it is excluded from --record and named as coincidence.
        scored = [h for h in scored if h.get("status") == "candidate"]
        scored.sort(key=lambda i: (-(i.get("match_weight") or 0.0),
                                   -i["match_confidence"], i["id"]))
        if not scored:
            results.append({"held_out": held["id"], "outcome": "silent"})
            continue
        top = scored[0]
        results.append({
            "held_out": held["id"],
            "outcome": "transferred" if top["id"] in peers else "wrong_family",
            "returned": top["id"],
            "peers_available": len(peers),
            "confidence_it_reports": top["match_confidence"],
        })

    counts = {k: sum(1 for r in results if r["outcome"] == k)
              for k in ("transferred", "wrong_family", "silent")}
    seen = sorted(r["confidence_it_reports"] for r in results
                  if r.get("confidence_it_reports") is not None)
    conf_summary = {
        "n": len(seen),
        "min": seen[0] if seen else None,
        "median": seen[len(seen) // 2] if seen else None,
        "max": seen[-1] if seen else None,
    } if seen else None
    payload = {
        "mode": "holdout-retrieval",
        "cards_total": len(cards),
        "cards_measurable": measured,
        "note": ("measurable means the handout is still on disk; the rest cannot be "
                 "held out, so this is a floor on the library, not a verdict on it"),
        "counts": counts,
        "transfer_rate": round(counts["transferred"] / measured, 3) if measured else None,
        "wrong_family_rate": round(counts["wrong_family"] / measured, 3) if measured else None,
        "silent_rate": round(counts["silent"] / measured, 3) if measured else None,
        "abstained": counts["silent"],
        "confidence_on_phantom": conf_summary,
        "reading": ("abstained is the number of times the index correctly said it "
                    "had nothing. confidence_on_phantom is what it claimed instead. "
                    "related_rate is a crude floor: the wording overlap scores some "
                    "genuine transfer as unrelated, so compare runs with it, do not "
                    "conclude from it."),
        "results": sorted(results, key=lambda r: r["outcome"]),
    }
    print(json.dumps(payload, ensure_ascii=False,
                     indent=None if args.json else 2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
