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


OPENING_STAGES = ("recon", "primitive")


def opening_text(card):
    """The move that gets purchase, not the one that gets the flag.

    AGENTS.md section 5: "a note belongs to the class whose first probe opens
    the chain, not the class of the final payload." This function is what makes
    that rule reachable; the docstring of --into already admitted the old
    behaviour broke it.
    """
    steps = card.get("chain", [])
    opening = [s.get("action", "") for s in steps if s.get("stage") in OPENING_STAGES]
    if not opening and steps:
        opening = [steps[0].get("action", "")]
    return "\n".join(opening)


def _rank_text(text, classes):
    hits = classifier.scan_text(text, classifier.compile_signals(classes, "observation_signals"),
                               limit_per_class=8)
    for class_id, evidence in classifier.scan_text(
            text, classifier.compile_signals(classes, "source_signals"), limit_per_class=8).items():
        hits.setdefault(class_id, []).extend(evidence)
    return classifier.rank(hits, classes, classifier.load_signal_stats())


def classify_card(card, taxonomy):
    """Classify from the card's own signals and its solved note, nothing else.

    The opening stages are ranked first and on their own. Scoring the whole card
    at once lets the final payload decide: a chain that opens on "a recursive
    merge whose destination is an object" filed as SSRF, one opening on "bcrypt
    hashes only the first 72 bytes" filed as request smuggling, one opening on
    "f-strings inside query construction" filed as SSTI. The exploit narrative
    carries the loud vocabulary — RCE, pickle, template — and outvoted the quiet
    sentence that actually says where the chain starts.

    The full text is still ranked, and is used when the opening stages name no
    class at all, so a card whose opener is written vaguely still gets filed.
    """
    classes = taxonomy["classes"]
    opening = _rank_text(opening_text(card), classes)
    if opening:
        return opening

    parts = list(card.get("signals", [])) + list(card.get("stack", []))
    for step in card.get("chain", []):
        parts.append(step.get("action", ""))
    note_path = os.path.join(ROOT, card["source_note"])
    if os.path.isfile(note_path):
        with open(note_path, encoding="utf-8", errors="replace") as handle:
            parts.append(handle.read())
    return _rank_text("\n".join(parts), classes)


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
    if primary.get("operator_override"):
        lines.append("- filed by operator override: the matcher did not rank this class; "
                     "the chain is filed under the class whose first probe opens it")
    else:
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
            # --into is the operator's decision and outranks the matcher. The
            # matcher scores the prose of the solved note, so a chain whose first
            # probe opens one class often ranks under the class of its final
            # payload; refusing the override there filed solves under the wrong
            # skill. Any class in the taxonomy is allowed, and the entry records
            # that no signal matched automatically.
            known = next((c for c in taxonomy["classes"] if c["id"] == args.into), None)
            if known is None:
                raise SystemExit(json.dumps({
                    "error": "--into names a class that is not in the taxonomy",
                    "requested": args.into,
                    "known": sorted(c["id"] for c in taxonomy["classes"])}, indent=2))
            primary = {"class": args.into, "score": 0.0, "signals_matched": 0,
                       "coverage": 0.0, "evidence": [],
                       "evidence_level": known["evidence_level"],
                       "operator_override": True}
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
    if not os.access(path, os.W_OK):
        raise SystemExit(json.dumps({
            "error": "field-notes.md is not writable, so the solve cannot be filed",
            "path": os.path.relpath(path, ROOT),
            "mode": oct(os.stat(path).st_mode & 0o777),
            "why": ("the learning loop stops here silently unless this is fixed; a restored "
                    "or copied tree often arrives with read-only notes"),
            "fix": "chmod u+w skills/*/field-notes.md",
        }, ensure_ascii=False, indent=2))
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


GENERATOR = os.path.join(ROOT, "build", "make_bug_classes.py")
LIVE_STATUSES = ("verified_live", "verified_artifact")


def cmd_promote(class_id, chain_id, taxonomy):
    """Raise a class from catalogue to verified, against the card that proves it.

    CLAUDE.md lists hand-editing bug-classes.json as a trap: "the label rises
    only through a chain card and classify_solve, never by editing". There was
    no such path in classify_solve, so the only way to promote was the forbidden
    one, and nobody took it — web-xxe and web-logic-flaw each hold a
    verified_live chain card in their own field notes while still telling the
    agent "this toolkit has never solved one", which AGENTS.md then instructs it
    to weight down. This is the missing path. It refuses unless the evidence is
    on disk, and it edits the generator rather than its output.
    """
    entry = next((c for c in taxonomy["classes"] if c["id"] == class_id), None)
    if entry is None:
        raise SystemExit(json.dumps({"error": "unknown class", "class": class_id}))
    if entry["evidence_level"] != "catalogue":
        raise SystemExit(json.dumps({"skipped": "already %s" % entry["evidence_level"],
                                     "class": class_id,
                                     "verified_by": entry.get("verified_by", [])}))
    card_path = os.path.join(ROOT, "knowledge", "chains", chain_id + ".json")
    if not os.path.isfile(card_path):
        raise SystemExit(json.dumps({"error": "no such chain card", "chain": chain_id}))
    with open(card_path, encoding="utf-8") as handle:
        card = json.load(handle)
    status = (card.get("verification") or {}).get("status")
    if status not in LIVE_STATUSES:
        raise SystemExit(json.dumps({
            "error": "chain card is not verified against a live response or artifact",
            "chain": chain_id, "status": status, "accepted": list(LIVE_STATUSES)}))
    notes = notes_path(class_id, taxonomy)
    cites = os.path.isfile(notes) and chain_id in open(notes, encoding="utf-8").read()
    if not cites:
        raise SystemExit(json.dumps({
            "error": "the class's field notes do not cite this card, so the card is "
                     "not local experience for this class",
            "class": class_id, "chain": chain_id,
            "fix": "python3 tools/classify_solve.py --chain %s --into %s" % (chain_id, class_id)}))

    source = open(GENERATOR, encoding="utf-8").read()
    needle = '"id": "%s"' % class_id
    if needle not in source:
        raise SystemExit(json.dumps({"error": "class not defined in the generator",
                                     "class": class_id, "generator": "build/make_bug_classes.py"}))
    old = '"evidence_level": "catalogue", "verified_by": [],'
    start = source.index(needle)
    end = source.find('"id": "', start + len(needle))
    block = source[start:end if end != -1 else len(source)]
    if old not in block:
        raise SystemExit(json.dumps({"error": "generator block is not in the expected "
                                              "catalogue shape; promote by hand and say why",
                                     "class": class_id}))
    new = ('"evidence_level": "verified",\n'
           '        "verified_by": ["%s"],' % chain_id)
    source = source[:start] + block.replace(old, new, 1) + source[start + len(block):]
    with open(GENERATOR, "w", encoding="utf-8") as handle:
        handle.write(source)
    print(json.dumps({
        "promoted": class_id, "verified_by": chain_id,
        "evidence": {"card": os.path.relpath(card_path, ROOT), "status": status,
                     "cited_in": os.path.relpath(notes, ROOT)},
        "edited": "build/make_bug_classes.py",
        "next": ["python3 build/make_bug_classes.py",
                 "python3 build/make_class_skills.py",
                 "python3 build/make_registry.py",
                 "python3 build/make_index.py",
                 "python3 tools/skill_audit.py --apply",
                 "bash test/run_all.sh"],
    }, indent=2))
    return 0


def cmd_confirm(class_id, anchor, taxonomy):
    """Promote one entry to confirmed.

    The anchor is the solve date, so two solves filed on the same day collided
    and this refused with 'found: 2' and no way forward: 17 of 54 entries were
    unconfirmable, which is most of why the review queue never drained. An
    anchor may now be written 'DATE:challenge-name' to disambiguate, and an
    ambiguous plain date lists the exact commands that would work.
    """
    path = notes_path(class_id, taxonomy)
    text = open(path, encoding="utf-8").read()
    wanted_name = None
    if ":" in anchor:
        anchor, wanted_name = anchor.split(":", 1)
    matches = [m for m in ENTRY_HEAD.finditer(text) if m.group("anchor") == anchor]
    if wanted_name is not None:
        needle = wanted_name.strip().lower()
        matches = [m for m in matches if needle in m.group("name").strip().lower()]
    if len(matches) != 1:
        detail = {"error": "anchor must identify exactly one entry",
                  "anchor": anchor, "found": len(matches)}
        if len(matches) > 1:
            detail["candidates"] = [m.group("name").strip() for m in matches]
            detail["disambiguate_with"] = [
                "python3 tools/classify_solve.py --confirm %s %s:%s"
                % (class_id, anchor, m.group("name").strip()) for m in matches]
        raise SystemExit(json.dumps(detail, ensure_ascii=False, indent=2))
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
    group.add_argument("--promote", nargs=2, metavar=("CLASS", "CHAIN_ID"),
                       help="raise a catalogue class to verified against a chain card "
                            "that proves it; refuses unless the card is verified_live "
                            "and cited in that class's field notes")
    parser.add_argument("--into", help="force the target class instead of the top candidate")
    parser.add_argument("--dry-run", action="store_true", help="print the entry, write nothing")
    args = parser.parse_args()
    taxonomy = classifier.load_taxonomy(TAXONOMY)
    if args.review:
        return cmd_review(taxonomy)
    if args.promote:
        return cmd_promote(args.promote[0], args.promote[1], taxonomy)
    if args.confirm:
        return cmd_confirm(args.confirm[0], args.confirm[1], taxonomy)
    return cmd_record(args, taxonomy)


if __name__ == "__main__":
    sys.exit(main())
