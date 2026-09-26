#!/usr/bin/env python3
"""Audit every skill for actionability and flag generic ones.

A generic skill talks only in generalities: no first probe, no
falsifier, no traps, no local evidence, or content so diluted it overlaps a
neighbour skill. This tool scores each skill on structural proxies for those
properties and reports; it never edits or deletes anything.

Layers are audited differently on purpose:
- entry/router skills are thin by design; only bloat is flagged
- depth skills that are not bug classes are judged as references: they must
  carry commands (code fences or inline code)
- bug-class skills carry the full score, and both real formats are accepted:
  the class-split format ("First probe", "Falsifier") and the rewritten depth
  format ("First probes:", budget stop_conditions, a Discipline section)

Score (bug-class skills only), 0-100:
  15  a first probe exists ("First probe" / "First probes:")
  15  a falsifier or budget stop_conditions exist
  15  traps / pitfalls / a Discipline section exist
  10  field-notes.md carries content (>= 20 lines; a 16-line template stub
      means no local experience has landed in this class yet)
  10  evidence honesty: verified skills name chain cards, catalogue skills
      state they are standard published knowledge
  10  sane size: 30-400 lines
  15  specificity: nearest-neighbour 5-gram overlap < 50%
      (0.5-0.7 half credit, > 0.7 zero and flagged as diluted)

Verdicts: >= 75 pass, 60-74 warn, < 60 review (the trash list).
"""
import argparse
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS, WARN, REVIEW = 75, 60, 0


def shingles(text, size=5):
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(tokens[i:i + size]) for i in range(len(tokens) - size + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load(path, fallback):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return fallback


def audit():
    registry = load(os.path.join(ROOT, "skills", "registry.json"),
                    {"skills": []})
    taxonomy = load(os.path.join(ROOT, "knowledge", "bug-classes.json"),
                    {"classes": []})
    verified = {c["id"] for c in taxonomy.get("classes", [])
                if c.get("evidence_level") == "verified"}
    catalogue = {c["id"] for c in taxonomy.get("classes", [])
                 if c.get("evidence_level") == "catalogue"}
    bug_class_ids = {c["id"] for c in taxonomy.get("classes", [])}

    depth_texts = {}
    rows = []
    for entry in registry.get("skills", []):
        rel = entry.get("path", "")
        full = os.path.join(ROOT, rel)
        row = {"id": entry.get("id"), "layer": entry.get("layer"),
               "path": rel, "flags": [], "score": None, "verdict": None,
               "local_evidence": "not-applicable"}
        rows.append(row)
        if not os.path.isfile(full):
            row["verdict"] = "missing"
            row["flags"].append("skill file does not exist")
            continue
        with open(full, encoding="utf-8") as handle:
            text = handle.read()
        lines = text.count("\n") + 1
        row["lines"] = lines
        layer = entry.get("layer")

        if layer in ("entry", "router"):
            # Routers are thin by design, but "thin" is not "empty". A router has
            # one job: give the first command, then say where to go next. Before
            # this floor existed the branch only checked for bloat, and
            # pwn-binary-triage sat at 11 lines with no probe and no routing
            # table, scoring pass.
            row["verdict"] = "thin-by-design"
            low = text.lower()
            targets = len(re.findall(r"[a-z0-9_.-]+\.md", text))
            table_rows = len([ln for ln in text.splitlines()
                              if ln.startswith("|") and ln.count("|") >= 3])
            if lines > 160:
                row["verdict"] = "warn"
                row["flags"].append("router/entry bloated: %d lines" % lines)
            if lines < 25:
                row["verdict"] = "warn"
                row["flags"].append("router/entry too thin to route: %d lines" % lines)
            if "first probe" not in low:
                row["verdict"] = "warn"
                row["flags"].append("no first probe")
            if targets < 3 and table_rows < 3:
                row["verdict"] = "warn"
                row["flags"].append("no routing table: %d named files, %d table rows"
                                    % (targets, table_rows))
            continue

        if entry.get("id") not in bug_class_ids:
            # A depth skill that is not a bug class (ctf-*, tool how-tos):
            # judged as a reference — it must carry commands, and it must say
            # when to stop reading it.
            row["verdict"] = "reference"
            fences = text.count("```")
            inline = len(re.findall(r"`[^`\n]+`", text))
            if fences < 3 and inline < 10:
                row["verdict"] = "warn"
                row["flags"].append("reference skill carries too few "
                                    "commands (%d fences, %d inline)"
                                    % (fences, inline))
            # Every bug-class skill carries a budget and a stop condition, and
            # the regression suite enforces it. The category corpora carried
            # neither, though they are the files an agent can sink a whole
            # session into: ctf-pwn is ~114k tokens, ctf-reverse ~100k,
            # ctf-crypto ~100k, ctf-web ~97k. The discipline was attached to the
            # small files and missing from the large ones, which is backwards.
            low = text.lower()
            if entry.get("depth_tokens", 0) >= 5000:
                if "stop_conditions" not in low and "stop when" not in low:
                    row["verdict"] = "warn"
                    row["flags"].append("corpus of %d tokens with no stop condition"
                                        % entry.get("depth_tokens", 0))
                if "budget" not in low:
                    row["verdict"] = "warn"
                    row["flags"].append("corpus of %d tokens with no budget"
                                        % entry.get("depth_tokens", 0))
            continue

        # bug-class skill: full score. Two real formats are accepted: the
        # class-split format ("First probe", "Falsifier") and the rewritten
        # depth format ("First probes:", budget stop_conditions, Discipline).
        score = 0
        low = text.lower()
        if re.search(r"first probes?\b|first payload|## confirm\b", low):
            score += 15
        else:
            row["flags"].append("no first probe")
        if re.search(r"falsifier|stop_conditions|closes (this|the) class", low):
            score += 15
        else:
            row["flags"].append("no falsifier or stop conditions")
        if re.search(r"trap|pitfall|## discipline", low):
            score += 15
        else:
            row["flags"].append("no traps/pitfalls/discipline")
        if "## operational probe" in low:
            row["actionability"] = "operational"
        else:
            row["actionability"] = "basic"
            row["flags"].append("no operational probe contract")
        notes = os.path.join(os.path.dirname(full), "field-notes.md")
        if os.path.isfile(notes):
            with open(notes, encoding="utf-8") as handle:
                notes_lines = handle.read().count("\n")
        else:
            notes_lines = -1
        if notes_lines >= 20:
            score += 10
            row["local_evidence"] = "present"
        elif notes_lines >= 0:
            row["local_evidence"] = "stub"
            row["flags"].append("field-notes is a template stub "
                                "(%d lines)" % notes_lines)
        else:
            row["local_evidence"] = "missing"
            row["flags"].append("field-notes missing")
        if entry.get("id") in verified and re.search(
                r"knowledge/chains/|chains that prove", low):
            score += 10
        elif entry.get("id") in catalogue and (
                "standard published knowledge" in low or "catalogue" in low):
            score += 10
        else:
            row["flags"].append("no evidence honesty line")
        if 30 <= lines <= 400:
            score += 10
        elif lines < 30:
            row["flags"].append("stub: %d lines" % lines)
        else:
            row["flags"].append("bloated: %d lines" % lines)
        depth_texts[entry.get("id")] = shingles(text)
        row["score"] = score  # specificity added in the second pass

    # Second pass: nearest-neighbour overlap for depth skills.
    ids = list(depth_texts)
    neighbours = {}
    for skill_id in ids:
        best, best_ratio = None, 0.0
        for other in ids:
            if other == skill_id:
                continue
            ratio = jaccard(depth_texts[skill_id], depth_texts[other])
            if ratio > best_ratio:
                best, best_ratio = other, ratio
        neighbours[skill_id] = (best, round(best_ratio, 3))
    for row in rows:
        if row["score"] is None:
            continue
        skill_id = row["id"]
        best, ratio = neighbours.get(skill_id, (None, 0.0))
        row["nearest_neighbour"] = best
        row["overlap"] = ratio
        if ratio > 0.7:
            row["flags"].append("diluted: %.0f%% overlap with %s"
                                % (ratio * 100, best))
        elif ratio >= 0.5:
            row["score"] += 7
            row["flags"].append("high overlap: %.0f%% with %s"
                                % (ratio * 100, best))
        else:
            row["score"] += 15
        row["verdict"] = ("pass" if row["score"] >= PASS
                          else "warn" if row["score"] >= WARN else "review")
        row["trust"] = ("local-confirmed" if row["local_evidence"] == "present"
                         else "catalogue-or-unreviewed")

    flagged = [r["id"] for r in rows if r["verdict"] == "review"]
    warned = [r["id"] for r in rows if r["verdict"] == "warn"]
    return {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "thresholds": {"pass": PASS, "warn": WARN, "review_below": REVIEW},
            "summary": {"skills": len(rows), "review": len(flagged),
                        "warn": len(warned),
                        "local_evidence_present": sum(
                            r.get("local_evidence") == "present" for r in rows),
                        "local_evidence_stub": sum(
                            r.get("local_evidence") == "stub" for r in rows),
                        "local_evidence_missing": sum(
                            r.get("local_evidence") == "missing" for r in rows),
                        "actionable_skills": sum(
                            r.get("actionability") == "operational" for r in rows),
                        "basic_skills": sum(
                            r.get("actionability") == "basic" for r in rows)},
            "review": flagged, "warn": warned, "skills": rows}


def main():
    parser = argparse.ArgumentParser(
        description="Audit skills for actionability; flags generic ones")
    parser.add_argument("--apply", action="store_true",
                        help="write the report to knowledge/skill-audit.json")
    parser.add_argument("--json", action="store_true",
                        help="print the full report as JSON")
    args = parser.parse_args()
    report = audit()
    if args.apply:
        path = os.path.join(ROOT, "knowledge", "skill-audit.json")
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
        report["written_to"] = "knowledge/skill-audit.json"
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("skills audited: %d | review: %d | warn: %d"
              % (report["summary"]["skills"], report["summary"]["review"],
                 report["summary"]["warn"]))
        for row in report["skills"]:
            if row["verdict"] in ("review", "warn") or row["flags"]:
                print("[%s] %-28s score=%s lines=%s overlap=%s evidence=%s"
                      % (row["verdict"], row["id"], row["score"],
                         row.get("lines", "-"), row.get("overlap", "-"),
                         row.get("local_evidence", "-")))
                for flag in row["flags"]:
                    print("        - %s" % flag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
