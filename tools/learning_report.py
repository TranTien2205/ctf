#!/usr/bin/env python3
"""Report the operational learning backlog without changing repository state.

The report separates structural health from local evidence. A skill can pass the
static contract while still having no reviewed field note; that distinction is
important when deciding whether to trust it during a contest.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = re.compile(r"^## (?P<anchor>\S+) · (?P<name>.+?) · (?P<status>proposed|confirmed)$", re.M)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def report():
    taxonomy = load(ROOT / "knowledge" / "bug-classes.json")["classes"]
    rows = []
    proposed = confirmed = 0
    for cls in taxonomy:
        notes = ROOT / "skills" / cls["skill_dir"] / "field-notes.md"
        text = notes.read_text(encoding="utf-8") if notes.is_file() else ""
        entries = [{"anchor": m.group("anchor"), "challenge": m.group("name"),
                    "status": m.group("status")} for m in ENTRY.finditer(text)]
        p = sum(item["status"] == "proposed" for item in entries)
        c = sum(item["status"] == "confirmed" for item in entries)
        proposed += p
        confirmed += c
        rows.append({
            "class": cls["id"],
            "evidence_level": cls["evidence_level"],
            "field_notes": len(entries),
            "proposed": p,
            "confirmed": c,
            "local_confidence": "confirmed" if c else "proposed" if p else "none",
            "review_command": ("python3 tools/classify_solve.py --confirm %s <anchor>"
                               % cls["id"]) if p else None,
        })
    misses_path = ROOT / "knowledge" / "classify-misses.log"
    miss_lines = [line for line in misses_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()] if misses_path.is_file() else []
    return {
        "summary": {
            "classes": len(rows),
            "verified_classes": sum(r["evidence_level"] == "verified" for r in rows),
            "catalogue_classes": sum(r["evidence_level"] == "catalogue" for r in rows),
            "field_notes": proposed + confirmed,
            "proposed_notes": proposed,
            "confirmed_notes": confirmed,
            "classify_miss_lines": len(miss_lines),
        },
        "review_queue": [r for r in rows if r["proposed"]],
        "classes": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Report the CTF learning backlog")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = report()
    print(json.dumps(payload, ensure_ascii=False, indent=None if args.json else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
