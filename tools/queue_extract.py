#!/usr/bin/env python3
"""Score normalized writeups and produce an evidence-first extraction queue."""
import argparse
import glob
import json
import os
import re

TECH = re.compile(r"sqli|sql injection|xss|ssrf|ssti|csrf|deserialize|unserialize|lfi|rfi|traversal|upload|jwt|cookie|session|header|request|response|curl|payload|exploit|vulnerab", re.I)
CODE = re.compile(r"```|`[^`]+`|\b(?:SELECT|UNION|curl|wget|python|php|javascript|GET |POST )\b", re.I)


def main():
    ap = argparse.ArgumentParser(description="Build extraction queue from normalized writeups")
    ap.add_argument("source_dir")
    ap.add_argument("--min-score", type=int, default=5)
    args = ap.parse_args()
    rows = []
    for path in glob.glob(os.path.join(args.source_dir, "normalized", "*.md")):
        text = open(path, encoding="utf-8", errors="replace").read()
        score = min(len(text) // 500, 6) + min(len(TECH.findall(text)), 8) + min(len(CODE.findall(text)), 6)
        reasons = []
        if len(text) >= 1200:
            reasons.append("substantial-text")
        if TECH.search(text):
            reasons.append("technique-signal")
        if CODE.search(text):
            reasons.append("code-or-request")
        rows.append({"path": path, "sha256": os.path.basename(path).split(".")[0],
                     "bytes": len(text.encode()), "score": score, "reasons": reasons,
                     "decision": "extract" if score >= args.min_score and len(text) >= 500 else "raw-only"})
    rows.sort(key=lambda row: (-row["score"], -row["bytes"], row["path"]))
    output = os.path.join(args.source_dir, "extraction-queue.json")
    with open(output, "w", encoding="utf-8") as handle:
        json.dump({"min_score": args.min_score, "documents": rows}, handle, ensure_ascii=False, indent=2)
    print(json.dumps({"queue": output, "total": len(rows),
                      "extract": sum(row["decision"] == "extract" for row in rows),
                      "raw_only": sum(row["decision"] == "raw-only" for row in rows)}))


if __name__ == "__main__":
    main()
