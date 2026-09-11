#!/usr/bin/env python3
"""Measure routing only; this is not solving accuracy."""
import json
import os
import subprocess
import sys
import time
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    cases = json.load(open(os.path.join(ROOT, "golden.json"), encoding="utf-8"))
    correct = 0
    timings = []
    for case in cases:
        started = time.monotonic()
        from ctf import observation_route
        result = observation_route(case["text"])
        timings.append(time.monotonic() - started)
        actual = (result.get("route") or {}).get("category")
        correct += actual == case["category"]
    ordered = sorted(timings)
    p50 = statistics.median(ordered)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    print(json.dumps({"scope": "routing_only", "cases": len(cases), "correct": correct, "accuracy": correct / len(cases),
                      "avg_seconds": sum(timings) / len(timings), "p50_seconds": p50,
                      "p95_seconds": p95, "measurement": "in-process"}, ensure_ascii=False))
    return 0 if correct == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
