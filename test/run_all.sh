#!/usr/bin/env bash
# The gate. Every change passes this before it is accepted.
#
# Four layers, cheapest first, and each one answers a different question:
#
#   unit         is the control plane correct in isolation?
#   consistency  does the system still agree with itself — registries, docs, tools?
#   harness      does the agent loop wire a model to the broker and the ledger?
#   e2e          does the whole stack prove real vulnerabilities on a real target?
#   baselines    does the measurement harness still run? It produces numbers rather
#                than assertions, and a measurement harness that silently stops
#                working is worse than not having one.
#
# No network and no model is required: the e2e layer runs against the fixture in
# test/fixtures/vulnapp.py, bound to loopback. Set ARGUS_SKIP_E2E=1 to skip the
# slowest layer while iterating, and never to make the gate pass.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export ARGUS_ENGAGEMENTS="${ARGUS_ENGAGEMENTS:-$ROOT/engagements}"

FAILED=()
run() {
    local label="$1"; shift
    local started elapsed status output
    started=$(date +%s)
    printf '\n\033[1m== %s ==\033[0m\n' "$label"
    output=$("$@" 2>&1); status=$?
    elapsed=$(( $(date +%s) - started ))
    if [ $status -eq 0 ]; then
        printf '%s\n' "$output" | tail -3
        printf '\033[32mPASS\033[0m %s (%ss)\n' "$label" "$elapsed"
    else
        printf '%s\n' "$output" | tail -40
        printf '\033[31mFAIL\033[0m %s (%ss, exit %s)\n' "$label" "$elapsed" "$status"
        FAILED+=("$label")
    fi
}

printf 'argus gate — %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'python %s\n' "$(python3 -V 2>&1)"

run "unit: control plane"        python3 -u test/unit.py
run "consistency: the system agrees with itself" python3 -u test/consistency.py
run "harness: the agent loop"    python3 -u test/harness_loop.py
if [ "${ARGUS_SKIP_E2E:-0}" != "1" ]; then
    run "e2e: the fixture, end to end" python3 -u test/e2e_fixture.py
    run "baselines: the measurement harness runs" python3 -u test/baselines.py --json
else
    printf '\n\033[33mSKIPPED\033[0m e2e and baselines (ARGUS_SKIP_E2E=1) — a skipped layer is not a pass\n'
fi

printf '\n'
if [ ${#FAILED[@]} -eq 0 ]; then
    printf '\033[32mgate passed\033[0m\n'
    exit 0
fi
printf '\033[31mgate failed:\033[0m %s\n' "${FAILED[*]}"
exit 1
