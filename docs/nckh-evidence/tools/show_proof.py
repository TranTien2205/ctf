"""Print the two proofs the supervisor asked for, straight from findings.json."""
import json
import sys

for f in json.load(open(sys.argv[1], encoding="utf-8")):
    if f["vuln_class"] in ("rce", "sqli"):
        print(f"{f['id']}  {f['vuln_class']:5s} grade={f['grade']}")
        print("     bang chung:", repr(f["evidence_excerpt"])[:80])
        for c in f["proof"]["checks"]:
            print(("     PASS " if c["ok"] else "     FAIL ") + c["check"])
