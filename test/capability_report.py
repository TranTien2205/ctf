#!/usr/bin/env python3
"""Print what this system can currently do, and optionally record it as the floor.

`test/baseline.json` is the floor the regression suite refuses to fall below.
Record a new baseline only after `bash test/run_all.sh` passes and the change has
been reviewed; the file is a claim about capability, so never raise it by hand.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from test.regression import CapabilityTests  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Capability snapshot for the CTF toolkit")
    parser.add_argument("--write", action="store_true", help="record the snapshot as the new floor")
    args = parser.parse_args()
    metrics = CapabilityTests.measure()
    report = {"metrics": metrics}
    if args.write:
        path = ROOT / "test" / "baseline.json"
        previous = {}
        if path.is_file():
            previous = json.loads(path.read_text(encoding="utf-8")).get("metrics", {})
        lowered = {k: (previous[k], metrics[k]) for k in previous
                   if k in metrics and metrics[k] < previous[k]}
        if lowered:
            print(json.dumps({"refused": "a metric would be lowered", "metrics": lowered}))
            return 1
        report["note"] = ("Floor for test/regression.py CapabilityTests. "
                          "Raise it only after run_all.sh passes.")
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"written": str(path.relative_to(ROOT)), "metrics": metrics}))
        return 0
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
