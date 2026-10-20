#!/usr/bin/env python3
"""Propose `classification.primary` for chain cards that carry no class label.

Why this exists. Measured on this tree: 49 of 72 chain cards had no
`classification.primary` at all. The card schema calls that field the
authoritative label and the only place a secondary class is recorded, so two
thirds of the library sat unattached to any taxonomy class.

That is not cosmetic. It blocks the one retrieval improvement that matters:

* `tools/chain_match.py` scores a card by matching the card's OWN signals, which
  are literal strings copied from that card's own handout -- a variable name, a
  path, a library version. A new challenge with the same MECHANISM has different
  literals, so the index matches on surface text rather than on mechanism. That
  is why `tools/holdout_eval.py` measures cross-challenge transfer at roughly
  zero while `tools/chain_match_eval.py` reports top-1 of 1.0: the second is a
  memory test, as its own docstring says.
* The generalising layer already exists. `knowledge/bug-classes.json` carries
  mechanism-level `source_signals` and `observation_signals` per class, and
  `tools/observation_eval.py` shows `tools/classify.py` generalises across the
  words a solver actually types. A two-stage retrieval -- classify to a class,
  then rank cards WITHIN that class -- would use it. It cannot be built while
  two thirds of the cards belong to no class.

What this tool is careful about. It REUSES `tools/classify.py`'s own scorer
(`compile_signals`, `scan_text`, `rank`) rather than inventing a second one, so
a backfilled label agrees with what the live classifier would say. It refuses
rather than guesses: a proposal needs a minimum score AND a margin over the
runner-up, and a near-tie is reported as `ambiguous` and left unlabelled. That
is the same stance `tools/classify_solve.py` takes on a tie, and leaving a card
unlabelled is a better outcome than attaching the wrong class to it.

A label this tool writes is marked `derived_by`, so it is never mistaken for one
a human reviewed. Promote it by reading the card and removing that marker.

    python3 tools/backfill_classification.py                 # report only
    python3 tools/backfill_classification.py --apply         # write confident ones
    python3 tools/backfill_classification.py --card <id>     # one card, verbose
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import classify as classifier  # noqa: E402

CHAINS = os.path.join(ROOT, "knowledge", "chains")
MARKER = "backfill_classification.py"

# A card's own prose is short, so a single generic signal can carry it. These
# floors were chosen against the 49 unlabelled cards: below them the top class
# was wrong as often as right, which is worse than leaving the card unlabelled.
MIN_SCORE = 2.0
MIN_MARGIN = 1.25      # the top class must beat the runner-up by this factor
MIN_SIGNALS = 2        # one matched signal is a coincidence, not a classification


def card_text(card):
    """The parts of a card that describe its MECHANISM, not its bookkeeping.

    `signals` and `chain` carry the mechanism. `id` and `source_note` carry the
    challenge's name, which would let a card match on its own filename rather
    than on what it did -- the same surface-text trap this tool exists to work
    around, so they are excluded.
    """
    parts = []
    for key in ("stack", "preconditions", "signals", "reuse_when", "known_traps"):
        value = card.get(key)
        if isinstance(value, list):
            parts.extend(str(v) for v in value)
        elif isinstance(value, dict):
            parts.extend("%s %s" % (k, v) for k, v in value.items())
        elif value:
            parts.append(str(value))
    for stage in card.get("chain") or []:
        if isinstance(stage, dict):
            for key in ("stage", "action", "mechanism", "observation", "why"):
                if stage.get(key):
                    parts.append(str(stage[key]))
        else:
            parts.append(str(stage))
    probe = card.get("first_confirming_probe")
    if isinstance(probe, dict):
        parts.extend(str(v) for v in probe.values())
    elif probe:
        parts.append(str(probe))
    return "\n".join(parts)


def load_cards():
    out = []
    for name in sorted(os.listdir(CHAINS)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(CHAINS, name)
        try:
            with open(path, encoding="utf-8") as handle:
                out.append((path, json.load(handle)))
        except (OSError, ValueError) as exc:
            out.append((path, {"_error": str(exc)}))
    return out


def classes_for(card, classes):
    """Only the classes in the card's OWN category may compete.

    Measured: adding sixteen crypto, pwn, rev, osint and misc classes gave the
    web cards new competitors that can win on a shared word. On
    `htb-amidst-us-imagemath-eval-static-folder` the reviewed label is
    `web-logic-flaw` and the tool answered `misc-interpreter-escape`, because
    `eval(` fires for both and the misc class has fewer signals so it reaches
    higher coverage. A chain card records its own category, so the fix is to
    read it rather than to tune a weight: a web solve is not evidence about a
    misc class.

    A card with no category competes against everything, which is the old
    behaviour and is reported as such.
    """
    category = ((card.get("challenge") or {}).get("category") or "").lower()
    if not category:
        return classes, None
    scoped = [c for c in classes if (c.get("category") or "web").lower() == category]
    if not scoped:
        # A category the taxonomy does not cover yet. Competing against every
        # class would invent a label from another category, so refuse instead.
        return [], category
    return scoped, category


def propose(card, classes, stats):
    """Rank the taxonomy against one card's mechanism text.

    Returns a dict with a verdict: `propose`, `ambiguous` or `none`. The reason
    is always stated, because a refusal that does not say why is indistinguish-
    able from a tool that is not working.
    """
    text = card_text(card)
    if not text.strip():
        return {"verdict": "none", "reason": "the card carries no mechanism prose to match"}

    scoped, category = classes_for(card, classes)
    if not scoped:
        return {"verdict": "none", "category": category,
                "reason": "the taxonomy has no class in category %r, so any label "
                          "would come from another category" % category}
    classes = scoped

    # Both signal families: a chain card's prose reads like an observation in
    # places and like source in others, and restricting to one halves the recall.
    hits = {}
    for field in ("source_signals", "observation_signals"):
        for class_id, bucket in classifier.scan_text(
                text, classifier.compile_signals(classes, field)).items():
            hits.setdefault(class_id, []).extend(bucket)
    if not hits:
        return {"verdict": "none", "reason": "no taxonomy signal fired on this card"}

    ranked = classifier.rank(hits, classes, stats)
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None

    detail = {
        "top": {"class": top["class"], "score": top["score"],
                "signals_matched": top["signals_matched"],
                "coverage": top["coverage"]},
        "runner_up": ({"class": second["class"], "score": second["score"]}
                      if second else None),
        "considered": [r["class"] for r in ranked[:5]],
    }

    if top["signals_matched"] < MIN_SIGNALS:
        detail.update(verdict="none",
                      reason="only %d signal matched; one signal is a coincidence"
                             % top["signals_matched"])
        return detail
    if top["score"] < MIN_SCORE:
        detail.update(verdict="none",
                      reason="top score %.2f is below the floor of %.2f"
                             % (top["score"], MIN_SCORE))
        return detail
    if second and second["score"] > 0 and top["score"] < second["score"] * MIN_MARGIN:
        detail.update(verdict="ambiguous",
                      reason="%s (%.2f) does not beat %s (%.2f) by the %.2fx margin, "
                             "so the evidence does not decide between these classes"
                             % (top["class"], top["score"], second["class"],
                                second["score"], MIN_MARGIN))
        return detail

    # Confidence is reported as what it is: a margin over the runner-up, scaled
    # into 0..1 for the schema's field. It is not a probability.
    margin = (top["score"] / second["score"]) if second and second["score"] else 3.0
    confidence = round(min(0.80, 0.45 + 0.12 * (margin - MIN_MARGIN)), 2)
    detail.update(verdict="propose", primary=top["class"], confidence=confidence,
                  secondary=[r["class"] for r in ranked[1:3]
                             if r["score"] >= MIN_SCORE],
                  reason="%s beats %s by %.2fx on %d matched signals"
                         % (top["class"],
                            second["class"] if second else "nothing",
                            margin, top["signals_matched"]))
    return detail


def measure(classes, stats):
    """Score this tool against the labels a human actually reviewed.

    The 23 cards that carry a `classification.primary` with no `derived_by`
    marker are ground truth written by a reviewer, so they are the only honest
    way to say how good a proposal is. Reported rather than asserted, because a
    precision figure quoted once in a commit message rots immediately.
    """
    truth = []
    for _, card in load_cards():
        if "_error" in card:
            continue
        block = card.get("classification") or {}
        if block.get("primary") and not block.get("derived_by"):
            truth.append((card, block["primary"]))

    proposed = correct = in_top3 = 0
    misses = []
    for card, label in truth:
        result = propose(card, classes, stats)
        if label in (result.get("considered") or [])[:3]:
            in_top3 += 1
        if result["verdict"] != "propose":
            continue
        proposed += 1
        if result["primary"] == label:
            correct += 1
        else:
            misses.append({"card": card.get("id"), "reviewed": label,
                           "tool_said": result["primary"]})

    return {
        "ground_truth_cards": len(truth),
        "proposed_on": proposed,
        "refused_on": len(truth) - proposed,
        "correct": correct,
        "precision_on_proposals": round(correct / proposed, 3) if proposed else None,
        "reviewed_label_in_top_3": in_top3,
        "recall_at_3": round(in_top3 / len(truth), 3) if truth else None,
        "misses": misses,
        "reading": ("precision is what matters here: a wrong label actively "
                    "misdirects retrieval, while a refusal only leaves the card "
                    "where it already was. The refusals are the design working, "
                    "not a shortfall"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Propose classification.primary for unlabelled chain cards")
    ap.add_argument("--measure", action="store_true",
                    help="score the proposer against the human-reviewed labels "
                         "and print precision; writes nothing")
    ap.add_argument("--apply", action="store_true",
                    help="write the confident proposals into the cards")
    ap.add_argument("--card", help="only this chain id")
    ap.add_argument("--relabel", action="store_true",
                    help="also consider cards that already carry a primary; "
                         "a label a human reviewed is never overwritten")
    args = ap.parse_args(argv)

    taxonomy = classifier.load_taxonomy()
    classes = taxonomy["classes"]
    try:
        stats = classifier.load_signal_stats()
    except Exception:
        stats = None

    if args.measure:
        print(json.dumps({"mode": "backfill-measure",
                          **measure(classes, stats)},
                         ensure_ascii=False, indent=2))
        return 0

    proposals, written = [], 0
    counts = {"propose": 0, "ambiguous": 0, "none": 0, "already": 0, "unreadable": 0}

    for path, card in load_cards():
        if "_error" in card:
            counts["unreadable"] += 1
            continue
        if args.card and card.get("id") != args.card:
            continue
        existing = (card.get("classification") or {})
        if existing.get("primary") and not args.relabel:
            counts["already"] += 1
            continue
        if existing.get("primary") and not existing.get("derived_by"):
            # Reviewed by a human. 23 cards carry one and the schema calls it
            # authoritative; recomputing a weaker answer over it is the bug
            # tools/classify_solve.py already has.
            counts["already"] += 1
            continue

        result = propose(card, classes, stats)
        counts[result["verdict"]] = counts.get(result["verdict"], 0) + 1
        result["card"] = card.get("id")
        proposals.append(result)

        if args.apply and result["verdict"] == "propose":
            block = dict(existing)
            block["primary"] = result["primary"]
            block["confidence"] = result["confidence"]
            if result.get("secondary"):
                block["secondary"] = result["secondary"]
            block["derived_by"] = MARKER
            card["classification"] = block
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(card, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            written += 1

    payload = {
        "mode": "backfill-classification",
        "applied": bool(args.apply),
        "written": written,
        "counts": counts,
        "floors": {"min_score": MIN_SCORE, "min_margin": MIN_MARGIN,
                   "min_signals": MIN_SIGNALS},
        "note": ("a label written here is marked derived_by and is NOT a reviewed "
                 "label; read the card and drop the marker to promote it. An "
                 "ambiguous card is left unlabelled on purpose"),
        "proposals": proposals,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
