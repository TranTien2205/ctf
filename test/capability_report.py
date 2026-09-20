#!/usr/bin/env python3
"""Print what this system can currently do, and optionally record it as the floor.

`test/baseline.json` is the floor the regression suite refuses to fall below.
Record a new baseline only after `bash test/run_all.sh` passes and the change has
been reviewed; the file is a claim about capability, so never raise it by hand.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_regression():
    """Load test/regression.py by path.

    Importing it as ``test.regression`` works only while ``test/__init__.py``
    exists and this directory shadows the standard library's own ``test``
    package. That is a trap: delete one empty file and the update gate starts
    reporting PASS while this report silently fails. Loading by path removes the
    dependency entirely.
    """
    spec = importlib.util.spec_from_file_location(
        "ctf_regression", ROOT / "test" / "regression.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CapabilityTests = _load_regression().CapabilityTests


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
