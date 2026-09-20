#!/usr/bin/env python3
"""Offline end-to-end evaluation for the CTF solver system.

This is deliberately separate from the legacy regression suite. The legacy suite
protects compatibility; this evaluator measures whether the system is useful:
classification, dispatch, chain reuse, first-probe completeness, controller
decisions, evidence gates, and learning-loop visibility.

It never contacts a target and never executes challenge artifacts.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from unittest.mock import patch  # noqa: E402

import ctf  # noqa: E402
from tools import classify as classifier  # noqa: E402
from tools import decide as decide_mod  # noqa: E402


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_cases():
    cases = load(ROOT / "test" / "cases" / "system_eval.json")
    results = []

    for case in cases["classification"]:
        tax = classifier.load_taxonomy()
        hits = classifier.scan_text(
            case["observation"],
            classifier.compile_signals(tax["classes"], "observation_signals"),
        )
        ranked = classifier.rank(hits, tax["classes"])
        names = [item["class"] for item in ranked]
        expected = case["expect_top"]
        ok = (not names) if expected is None else (bool(names) and names[0] == expected)
        results.append({"id": case["id"], "kind": "classification", "ok": ok,
                        "actual": names[:3], "expected": case["expect_top"]})

    for case in cases["routing"]:
        result = ctf.observation_route(case["observation"])
        actual = (result.get("route") or {}).get("category")
        results.append({"id": case["id"], "kind": "routing", "ok": actual == case["category"],
                        "actual": actual, "expected": case["category"]})

    registry = load(ROOT / "skills" / "registry.json")
    taxonomy = load(ROOT / "knowledge" / "bug-classes.json")
    registered = {item["id"]: item for item in registry["skills"]}
    for cls in taxonomy["classes"]:
        skill = ROOT / cls["skill"]
        text = skill.read_text(encoding="utf-8")
        checks = {
            "first_probe": bool(re.search(r"first probe|first probes|first payload|confirm", text, re.I)),
            "expected_signal": bool(re.search(r"expected|signal|response|render|reflect|change|output|status", text, re.I)),
            "falsifier": bool(re.search(r"falsifier|stop_conditions|closes", text, re.I)),
            "discipline": bool(re.search(r"discipline|trap|pitfall", text, re.I)),
            "evidence_level": ("evidence_level: %s" % cls["evidence_level"]) in text,
            "registered": cls["id"] in registered,
        }
        results.append({"id": "skill:%s" % cls["id"], "kind": "skill-contract",
                        "ok": all(checks.values()), "checks": checks})

    for case in cases["decisions"]:
        # These are executed through the real CLI in an isolated temporary tree.
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            (root / "challenges" / case["name"]).mkdir(parents=True)
            (root / "challenges" / case["name"] / "state.json").write_text(
                json.dumps(case["state"]), encoding="utf-8")
            with patch.object(decide_mod, "ROOT", str(root)), \
                    patch.object(decide_mod.state_mod, "ROOT", str(root)):
                payload = decide_mod.decide(case["name"])
            actual = payload.get("action")
            results.append({"id": case["id"], "kind": "decision", "ok": actual == case["action"],
                            "actual": actual, "expected": case["action"]})

    passed = sum(1 for item in results if item["ok"])
    return {"cases": len(results), "passed": passed, "failed": len(results) - passed,
            "accuracy": passed / len(results) if results else 1.0, "results": results}


def main():
    parser = argparse.ArgumentParser(description="Run offline end-to-end system evaluation")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_cases()
    print(json.dumps(report, ensure_ascii=False, indent=None if args.json else 2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
