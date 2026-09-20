#!/usr/bin/env python3
"""Close the loop: a verified solve becomes a field note in the right skill.

    python3 tools/classify_solve.py --chain <chain-card-id>      # after a solve
    python3 tools/classify_solve.py --review                     # list what awaits review
    python3 tools/classify_solve.py --confirm <class> <anchor>    # promote one entry

Every line written is copied from the chain card or the solved note. This tool
does not summarise, infer or invent: if the card does not say it, it is not
written. Entries land as `proposed` and stay that way until a human promotes
them, because an automatic write into a skill is how a skill quietly fills with
things nobody checked.

Raising a class from catalogue to verified is proposed here but never applied:
`knowledge/bug-classes.json` is edited by hand after review.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import classify as classifier  # noqa: E402

CHAINS = os.path.join(ROOT, "knowledge", "chains")
TAXONOMY = os.path.join(ROOT, "knowledge", "bug-classes.json")
STATUS_LINE = re.compile(r"^- status: (proposed|confirmed)\s*$", re.M)
ENTRY_HEAD = re.compile(r"^## (?P<anchor>\S+) · (?P<name>.+?) · (?P<status>proposed|confirmed)\s*$", re.M)


def load_chain(chain_id):
    path = os.path.join(CHAINS, chain_id + ".json")
    if not os.path.isfile(path):
        raise SystemExit(json.dumps({
            "error": "chain card not found", "id": chain_id,
            "available": sorted(os.path.splitext(f)[0] for f in os.listdir(CHAINS)
                                if f.endswith(".json"))}))
    with open(path, encoding="utf-8") as handle:
        card = json.load(handle)
    card["_path"] = os.path.relpath(path, ROOT)
    return card


def classify_card(card, taxonomy):
    """Classify from the card's own signals and its solved note, nothing else."""
    parts = list(card.get("signals", [])) + list(card.get("stack", []))
    for step in card.get("chain", []):
        parts.append(step.get("action", ""))
    note_path = os.path.join(ROOT, card["source_note"])
    if os.path.isfile(note_path):
        with open(note_path, encoding="utf-8", errors="replace") as handle:
            parts.append(handle.read())
    text = "\n".join(parts)
    classes = taxonomy["classes"]
    hits = classifier.scan_text(text, classifier.compile_signals(classes, "observation_signals"),
                               limit_per_class=8)
    for class_id, evidence in classifier.scan_text(
            text, classifier.compile_signals(classes, "source_signals"), limit_per_class=8).items():
        hits.setdefault(class_id, []).extend(evidence)
    return classifier.rank(hits, classes)


def render_entry(card, primary, others):
    probe = card.get("first_confirming_probe", {})
    lines = [
        "",
        "## %s · %s · proposed" % (card["challenge"].get("solved_at") or "undated",
                                   card["challenge"].get("name", "unnamed")),
        "",
        "- source note: `%s`" % card["source_note"],
        "- chain card: `%s`" % card["_path"],
        "- verification: %s — %s" % (card["verification"]["status"], card["verification"]["evidence"]),
        "- classified as: `%s` (score %s, %d signals matched)" % (
            primary["class"], primary["score"], primary["signals_matched"]),
    ]
    if others:
        lines.append("- also matched: " + ", ".join(
            "`%s` (%s)" % (o["class"], o["score"]) for o in others))
    lines.append("- signals that fired: " + ", ".join(
        sorted({item.get("matched") or item.get("signal") for item in primary["evidence"]})[:8]))
    if probe:
        lines += ["", "**Confirming probe that worked**", "",
                  "> " + probe.get("request", "").replace("\n", " "),
                  "",
                  "Expected: " + probe.get("expected", ""),
                  "",
                  "Falsifier: " + probe.get("falsifier", "")]
    if card.get("known_traps"):
        lines += ["", "**Traps recorded on this solve**", ""]
        lines += ["- " + trap for trap in card["known_traps"]]
    if card.get("blast_radius"):
        lines += ["", "**Blast radius**: " + card["blast_radius"]]
    lines += ["", "- status: proposed", ""]
    return "\n".join(lines)


def notes_path(class_id, taxonomy):
    for entry in taxonomy["classes"]:
        if entry["id"] == class_id:
            return os.path.join(ROOT, "skills", entry["skill_dir"], "field-notes.md")
    raise SystemExit(json.dumps({"error": "unknown class", "class": class_id}))


def cmd_record(args, taxonomy):
    card = load_chain(args.chain)
    ranked = classify_card(card, taxonomy)
    if not ranked:
        raise SystemExit(json.dumps({
            "error": "no class matched this card",
            "hint": "add signals to knowledge/bug-classes.json, or add a new class",
            "chain": card["_path"]}))
    if args.into:
        primary = next((r for r in ranked if r["class"] == args.into), None)
        if primary is None:
            raise SystemExit(json.dumps({
                "error": "--into names a class that did not match this card",
                "requested": args.into,
                "matched": [r["class"] for r in ranked]}))
    else:
        top = ranked[0]
        tied = [r for r in ranked
                if r["score"] == top["score"] and r["coverage"] == top["coverage"]]
        if len(tied) > 1:
            raise SystemExit(json.dumps({
                "error": "the evidence does not decide between these classes",
                "tied": [{"class": r["class"], "score": r["score"], "coverage": r["coverage"],
                          "signals": sorted({i.get("matched") or i.get("signal")
                                             for i in r["evidence"]})[:6]} for r in tied],
                "fix": ("decide from the chain card yourself, then re-run with "
                        "--into <class>. Guessing here would file the solve under the "
                        "wrong skill and the mistake would compound."),
            }, ensure_ascii=False, indent=2))
        primary = top
    others = [r for r in ranked if r["class"] != primary["class"]][:3]

    path = notes_path(primary["class"], taxonomy)
    if not os.path.isfile(path):
        raise SystemExit(json.dumps({"error": "field-notes.md missing", "path": path}))
    existing = open(path, encoding="utf-8").read()
    anchor = card["challenge"].get("solved_at") or "undated"
    if "## %s · %s ·" % (anchor, card["challenge"].get("name", "")) in existing:
        print(json.dumps({"skipped": "an entry for this challenge already exists",
                          "file": os.path.relpath(path, ROOT)}))
        return 0
    entry = render_entry(card, primary, others)
    if args.dry_run:
        print(entry)
        return 0
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(entry)

    result = {"written": os.path.relpath(path, ROOT), "class": primary["class"],
              "status": "proposed", "also_matched": [o["class"] for o in others]}
    if primary["evidence_level"] == "catalogue" and card["verification"]["status"] == "verified_live":
        result["proposal"] = (
            "class %s is marked catalogue but now has a verified_live chain card. "
            "After reviewing the entry, raise its evidence_level to verified in "
            "build/make_bug_classes.py, add %s to verified_by, regenerate, and run "
            "bash test/run_all.sh." % (primary["class"], card["id"]))
    result["next"] = ("review the entry, then: python3 tools/classify_solve.py --confirm %s %s"
                      % (primary["class"], anchor))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_review(taxonomy):
    pending = []
    for entry in taxonomy["classes"]:
        path = os.path.join(ROOT, "skills", entry["skill_dir"], "field-notes.md")
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        for match in ENTRY_HEAD.finditer(text):
            if match.group("status") == "proposed":
                pending.append({"class": entry["id"], "anchor": match.group("anchor"),
                                "challenge": match.group("name"),
                                "file": os.path.relpath(path, ROOT)})
    print(json.dumps({"awaiting_review": len(pending), "entries": pending,
                      "confirm_with": "python3 tools/classify_solve.py --confirm <class> <anchor>"},
                     ensure_ascii=False, indent=2))
    return 0


def cmd_confirm(class_id, anchor, taxonomy):
    path = notes_path(class_id, taxonomy)
    text = open(path, encoding="utf-8").read()
    matches = [m for m in ENTRY_HEAD.finditer(text) if m.group("anchor") == anchor]
    if len(matches) != 1:
        raise SystemExit(json.dumps({"error": "anchor must identify exactly one entry",
                                     "anchor": anchor, "found": len(matches)}))
    match = matches[0]
    if match.group("status") == "confirmed":
        print(json.dumps({"skipped": "already confirmed", "anchor": anchor}))
        return 0
    start = match.end()
    nxt = ENTRY_HEAD.search(text, start)
    end = nxt.start() if nxt else len(text)
    body = text[start:end]
    if "- status: proposed" not in body:
        raise SystemExit(json.dumps({"error": "entry body has no proposed status line"}))
    new_body = body.replace("- status: proposed", "- status: confirmed", 1)
    new_head = match.group(0).replace("· proposed", "· confirmed")
    updated = text[:match.start()] + new_head + new_body + text[end:]
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)
    print(json.dumps({"confirmed": anchor, "class": class_id,
                      "file": os.path.relpath(path, ROOT)}))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Turn a verified solve into a reviewed field note")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chain", metavar="ID", help="chain card id to record")
    group.add_argument("--review", action="store_true", help="list entries awaiting review")
    group.add_argument("--confirm", nargs=2, metavar=("CLASS", "ANCHOR"),
                       help="promote one entry to confirmed")
    parser.add_argument("--into", help="force the target class instead of the top candidate")
    parser.add_argument("--dry-run", action="store_true", help="print the entry, write nothing")
    args = parser.parse_args()
    taxonomy = classifier.load_taxonomy(TAXONOMY)
    if args.review:
        return cmd_review(taxonomy)
    if args.confirm:
        return cmd_confirm(args.confirm[0], args.confirm[1], taxonomy)
    return cmd_record(args, taxonomy)


if __name__ == "__main__":
    sys.exit(main())
