#!/usr/bin/env python3
"""Small independent integrity check for ~/ctf."""
import glob
import json
import os
import py_compile
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
checks = []


def check(name, ok, detail=""):
    checks.append((name, ok, detail))


check("ctf.py exists", os.path.isfile(os.path.join(ROOT, "ctf.py")))
check("PROMPT.md exists", os.path.isfile(os.path.join(ROOT, "PROMPT.md")))
check("knowledge schema exists", os.path.isfile(os.path.join(ROOT, "knowledge", "schema.json")))
check("first probes registry exists", os.path.isfile(os.path.join(ROOT, "knowledge", "first-probes.json")))
check("writeup schema exists", os.path.isfile(os.path.join(ROOT, "knowledge", "schema.json")))
check("operator workflow notes exist", os.path.isfile(os.path.join(ROOT, "agent", "autonomous-loop.md")))
check("probe policy exists", os.path.isfile(os.path.join(ROOT, "agent", "probe-policy.json")))
check("skill registry exists", os.path.isfile(os.path.join(ROOT, "skills", "registry.json")))
check("skill index exists", os.path.isfile(os.path.join(ROOT, "skills", "INDEX.md")))
check("chain schema exists", os.path.isfile(os.path.join(ROOT, "knowledge", "chain-schema.json")))
check("chain cards present", bool(glob.glob(os.path.join(ROOT, "knowledge", "chains", "*.json"))))
check("hypothesis protocol exists", os.path.isfile(os.path.join(ROOT, "HYPOTHESIS_PROTOCOL.md")))
check("update gate exists", os.path.isfile(os.path.join(ROOT, "test", "run_all.sh")))
check("version scripts exist", all(os.path.isfile(os.path.join(ROOT, "scripts", name))
                                   for name in ("repo_init.sh", "save_version.sh")))
check("external source lock exists", os.path.isfile(os.path.join(ROOT, "external", "sources.lock.json")))
for name in ("ctf.py", "selfcheck.py", "tools/skill_select.py", "tools/chain_match.py",
             "tools/import_external.py", "tools/state.py", "test/regression.py"):
    try:
        py_compile.compile(os.path.join(ROOT, name), doraise=True)
        check(name + " compiles", True)
    except Exception as exc:
        check(name + " compiles", False, str(exc))
proc = subprocess.run([sys.executable, os.path.join(ROOT, "ctf.py"), "--json", "RSA ciphertext modulus"],
                      capture_output=True, text=True)
try:
    result = json.loads(proc.stdout)
    check("blackbox route", result.get("route", {}).get("category") == "crypto")
except (ValueError, AttributeError):
    check("blackbox route", False, proc.stderr.strip())
planner = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "plan.py"), "--json", "private web URL PDF fetch"], capture_output=True, text=True)
try:
    plan = json.loads(planner.stdout)
    check("bounded first-probe plan", planner.returncode == 0 and plan.get("mode") == "first-probe-plan" and 1 <= len(plan.get("hypotheses", [])) <= 3)
except ValueError:
    check("bounded first-probe plan", False, planner.stderr.strip())
dispatch = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "skill_select.py"),
                           "--json", "web endpoint login cookie"], capture_output=True, text=True)
try:
    picked = json.loads(dispatch.stdout)
    routers = [item for item in picked.get("open_now", []) if item["layer"] == "router"]
    check("dispatcher returns exactly one router", len(routers) == 1 and not picked.get("problems"))
except ValueError:
    check("dispatcher returns exactly one router", False, dispatch.stderr.strip())
matcher = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "chain_match.py"),
                          "--json", "Express mongoose update noteId flag 403 access denied"],
                         capture_output=True, text=True)
try:
    matched = json.loads(matcher.stdout)
    check("chain matcher returns a candidate, not proof",
          bool(matched.get("candidates")) and matched["candidates"][0]["status"] == "candidate")
except ValueError:
    check("chain matcher returns a candidate, not proof", False, matcher.stderr.strip())
print("\n".join("[%s] %s%s" % ("PASS" if ok else "FAIL", name, " — " + detail if detail else "")
                 for name, ok, detail in checks))
passed = sum(ok for _, ok, _ in checks)
print("%d/%d PASS" % (passed, len(checks)))
sys.exit(0 if passed == len(checks) else 1)
