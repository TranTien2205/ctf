#!/usr/bin/env python3
"""Black-box recall of tools/classify.py, measured against real observations.

tools/system_eval.py already covers classification, but its cases are written in
the taxonomy's own vocabulary, so they pass whatever the signals look like. This
asks the harder question: when a solver types what they actually see, before any
source is available, does the classifier name the class?

Every case in test/baselines/observation_recall.json is either a chain verified
live in this repository or an ordinary phrasing of a class the taxonomy already
claims. A case passes when the expected class appears anywhere in the candidates;
`--strict` requires it at rank 1.
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = os.path.join(ROOT, "test", "baselines", "observation_recall.json")


def classify(observation):
    out = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "classify.py"), observation],
        capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        return None
    try:
        return [c["class"] for c in json.loads(out.stdout).get("candidates", [])]
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="require the expected class at rank 1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc = json.load(open(CASES, encoding="utf-8"))
    results, silent, wrong = [], 0, 0
    for case in doc["cases"]:
        got = classify(case["observation"])
        want = case.get("expect")
        if got is None:
            verdict = "error"
        elif want is None:
            # A negative case: this observation is out of scope (non-web) or is
            # an ordinary application, and silence is the correct answer. These
            # exist so recall cannot be bought by widening signals until
            # everything matches something.
            verdict = "hit" if not got else "false-positive"
            if not got:
                silent += 1
        elif not got:
            verdict = "silent"
            silent += 1
        elif args.strict:
            verdict = "hit" if got[0] == want else "miss"
        else:
            verdict = "hit" if want in got else "miss"
        if verdict in ("miss", "false-positive"):
            wrong += 1
        results.append({"id": case["id"], "expect": case["expect"],
                        "got": got, "verdict": verdict})

    hits = sum(1 for r in results if r["verdict"] == "hit")
    n = len(results)
    payload = {
        "mode": "observation-recall",
        "strict": args.strict,
        "cases": n,
        "hits": hits,
        "recall": round(hits / n, 3) if n else None,
        "silent": silent,
        "wrong_class": wrong,
        "reading": ("silent is the failure that matters: the classifier returned nothing at all, "
                    "so the controller has no class to open and the solver is back to guessing. "
                    "wrong_class at least gives a branch to falsify."),
        "results": results,
    }
    print(json.dumps(payload, indent=None if args.json else 2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
