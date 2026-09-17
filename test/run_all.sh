#!/usr/bin/env bash
# Update gate for ~/ctf. Run this before accepting any change to the system, and
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

hr "OPTIONAL: foundation tests (need jsonschema and tornado)"
if "$PY" -c "import jsonschema, tornado" 2>/dev/null; then
  "$PY" -m unittest discover -s tests || fail=1
else
  echo "SKIPPED: install jsonschema and tornado to run the foundation suite"
  echo "         pip install --break-system-packages jsonschema tornado"
fi

hr "CAPABILITY SNAPSHOT (compared against test/baseline.json by the regression suite)"
"$PY" test/capability_report.py

hr "RESULT"
if [ "$fail" -eq 0 ]; then
  echo "PASS — the change may be committed. Tag it with scripts/save_version.sh."
else
  echo "FAIL — do not commit. Fix the failure or revert to the last tag."
fi
exit "$fail"
