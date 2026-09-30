#!/usr/bin/env bash
# Update gate for this tree. Run it before accepting any change to the system, and
# again before committing. Required checks must pass; optional checks depend on
# packages that may not be installed and are reported without failing the gate.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2
PY="${PYTHON:-python3}"
fail=0

hr() { printf '\n== %s ==\n' "$1"; }

hr "REQUIRED: system regression (structure, contract, routing, dispatch, chains, ledger)"
"$PY" test/regression.py || fail=1

hr "REQUIRED: self check"
"$PY" selfcheck.py || fail=1

hr "REQUIRED: routing evaluator"
"$PY" tools/evaluate.py || fail=1

hr "REQUIRED: scope boundary (jeopardy CTF only, no machine or AD methodology)"
"$PY" tools/check_boundary.py || fail=1

hr "REQUIRED: end-to-end offline system evaluation (actionability, dispatch, skills, decisions)"
if ! "$PY" tools/system_eval.py --json; then fail=1; fi

hr "REQUIRED: learning-loop report"
if ! "$PY" tools/learning_report.py --json; then fail=1; fi

hr "REQUIRED: tool-layer selftests (web, crypto, pwn, forensics, a-d primitives -- all offline)"
# These prove the primitives the agent is told to prefer over hand-rolled
# requests. They were shipped with selftests that the gate never ran, so a
# regression in them would have been invisible here; measured at ~17s together.
# tools/ad is the attack-defense control plane; its selftest is pure-function
# only -- no sockets, no subprocess -- so it stays safe to run here.
for t in tools/web/selftest.py tools/crypto/selftest.py tools/pwnstatic/selftest.py tools/forensics/selftest.py tools/ad/selftest.py; do
  if [ -f "$t" ]; then
    printf -- '-- %s\n' "$t"
    "$PY" "$t" >/dev/null || { echo "FAILED: $t (run it directly for the detail)"; fail=1; }
  else
    echo "MISSING: $t"; fail=1
  fi
done

hr "REPORTED: chain transfer to an unseen challenge (a metric, not a contract)"
# chain_match_eval measures recall when the right card IS present and reads 1.0.
# This asks the other question -- hold a card out and see whether any card from
# the same mechanism family comes back -- and currently reads 0.042. It is
# printed rather than enforced because it is a number to move, not a floor to
# defend; a threshold here would only invite tuning the harness.
"$PY" tools/holdout_eval.py --json 2>/dev/null | "$PY" -c "import json,sys; d=json.load(sys.stdin); print('transfer=%s wrong_family=%s silent=%s over %s challenges' % (d['transfer_rate'], d['wrong_family_rate'], d['silent_rate'], d['cards_measurable']))" || echo "holdout_eval did not run"

hr "REQUIRED: subagent prompts are current with the evidence"
# A solve produces a chain card with traps and a first probe; without this the
# card never reaches the agent that needs it next, and the agent definitions
# quietly age. --check fails when any managed block is behind the cards.
"$PY" tools/agent_prompt_forge.py --check >/dev/null || { echo "FAILED: subagent prompts are stale -- run tools/agent_prompt_forge.py --apply"; fail=1; }

hr "REQUIRED: attack-defense subagent lint (offline)"
# The prohibitions in .claude/agents/ad-*.md are only real if something reads them
# back. Warnings do not fail: one deliberate FILL-IN has to survive until the
# estate's real path is known on the day.
if ! "$PY" tools/ad/agent_lint.py >/dev/null; then
  echo "FAILED: tools/ad/agent_lint.py (run it directly for the detail)"; fail=1
fi

hr "REQUIRED: web primitive selftests (--selftest on the tool itself -- all offline)"
# variant_matrix, race_probe, bundle_miner and session_dissect keep their checks
# behind their own --selftest flag, the pattern sanitizer_fuzz established, rather
# than in tools/web/selftest.py. 255 checks between them; each one exits non-zero
# when an assertion fails, and each was built by breaking the tool on purpose and
# confirming the check caught it.
for t in variant_matrix race_probe bundle_miner session_dissect; do
  f="tools/web/$t.py"
  if [ -f "$f" ]; then
    printf -- '-- %s --selftest\n' "$f"
    "$PY" "$f" --selftest >/dev/null || { echo "FAILED: $f --selftest"; fail=1; }
  else
    echo "MISSING: $f"; fail=1
  fi
done

hr "OPTIONAL: foundation tests (need jsonschema and tornado)"
if "$PY" -c "import jsonschema, tornado" 2>/dev/null; then
  "$PY" -m unittest discover -s tests || fail=1
else
  echo "SKIPPED: install jsonschema and tornado to run the foundation suite"
  echo "         pip install --break-system-packages jsonschema tornado"
fi

hr "REQUIRED: capability snapshot (compared against test/baseline.json by the regression suite)"
"$PY" test/capability_report.py || fail=1

hr "RESULT"
if [ "$fail" -eq 0 ]; then
  echo "PASS — the change may be committed. Tag it with scripts/save_version.sh."
else
  echo "FAIL — do not commit. Fix the failure or revert to the last tag."
fi
exit "$fail"
