#!/usr/bin/env python3
"""Small independent integrity check for this tree."""
import glob
import json
import os
import py_compile
import shutil
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
# The control plane. AGENTS.md makes this file the whole pre-flight — "fix any
# FAIL before starting" — while every check above it asked only whether a file
# exists or compiles. Nothing here ever executed decide.py or hooks.py, so an
# agent could open a session, be told the system was healthy, and discover
# mid-solve that the write gate was broken. By then, under this tree's own
# rules, no verdict it had recorded could be trusted.
LOOP_CHALLENGE = "selfcheck-control-loop"


def _run(*argv):
    return subprocess.run([sys.executable] + [os.path.join(ROOT, argv[0])] + list(argv[1:]),
                          capture_output=True, text=True)


try:
    shutil.rmtree(os.path.join(ROOT, "challenges", LOOP_CHALLENGE), ignore_errors=True)
    created = _run("tools/state.py", LOOP_CHALLENGE, "--category", "web",
                   "--target", "http://127.0.0.1:1/")
    added = _run("tools/state.py", LOOP_CHALLENGE, "--hypothesis",
                 "selfcheck hypothesis", "--bug-class", "web-ssti")
    hypothesis_id = json.loads(added.stdout)["state"]["hypotheses"][0]["id"]

    decision = _run("tools/decide.py", LOOP_CHALLENGE)
    action = json.loads(decision.stdout).get("action")
    check("decide.py returns an action", bool(action),
          "" if action else decision.stderr.strip()[:120])

    timeout_confirm = _run("tools/hooks.py", "post-probe", LOOP_CHALLENGE,
                           "--hypothesis-id", hypothesis_id, "--class", "web-ssti",
                           "--request", "curl -m 10 http://127.0.0.1:1/",
                           "--verdict", "confirms", "--evidence-kind", "class",
                           "--evidence", "curl: (28) Operation timed out after 10001 ms")
    ok = timeout_confirm.returncode != 0
    check("hooks.py refuses a timeout as a confirmation", ok,
          "" if ok else "a timeout was accepted as evidence of a bug class")

    surface_confirm = _run("tools/hooks.py", "post-probe", LOOP_CHALLENGE,
                           "--hypothesis-id", hypothesis_id, "--class", "web-ssti",
                           "--request", "GET /login",
                           "--verdict", "confirms", "--evidence-kind", "surface",
                           "--evidence", "200 OK, the login form rendered")
    ok = surface_confirm.returncode != 0
    check("hooks.py refuses surface evidence as a confirmation", ok,
          "" if ok else "a rendered form was accepted as proof of a bug class")

    self_confirm = _run("tools/state.py", LOOP_CHALLENGE,
                        "--hypothesis-id", hypothesis_id, "--status", "confirmed")
    reopened = _run("tools/decide.py", LOOP_CHALLENGE)
    got = json.loads(reopened.stdout).get("action")
    check("decide.py reopens a confirmation that bypassed the write gate",
          got == "reopen_confirm",
          "" if got == "reopen_confirm" else "decide.py answered %r instead" % got)
except Exception as exc:                      # a broken control plane must be loud
    check("control loop is executable", False, "%s: %s" % (type(exc).__name__, exc))
finally:
    shutil.rmtree(os.path.join(ROOT, "challenges", LOOP_CHALLENGE), ignore_errors=True)

print("\n".join("[%s] %s%s" % ("PASS" if ok else "FAIL", name, " — " + detail if detail else "")
                 for name, ok, detail in checks))
passed = sum(ok for _, ok, _ in checks)
print("%d/%d PASS" % (passed, len(checks)))
sys.exit(0 if passed == len(checks) else 1)
