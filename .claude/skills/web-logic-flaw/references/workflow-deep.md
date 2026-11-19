# Workflow deep — the business-logic engagement, with branch points

The shallow workflow (`workflow.md`) is the happy path. This module is
the same walk with the decision points rendered — what to do at each
branch the responses open.

## Phase 0 — recon the state machine

```bash
python3 tools/web/bundle_miner.py --url <bundle-url> --out /tmp/bundle
```

Read three files: `endpoints.txt` (the edge list), `secrets.txt`
(candidates — verify before use), and the reconstructed sources (the
imagined workflow, in code). Sort endpoints into create / transition /
terminal.

**Branch**: no bundle → the endpoint list comes from crawling the UI and
recording every form's action + every fetch/XHR in devtools. Sparse apps
may have only the flow's own endpoints.

## Phase 1 — classify, match, route

```bash
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --record <name>
python3 tools/skill_select.py web-logic-flaw
```

**Branch — a chain card matches**: read it; run its
`first_confirming_probe` verbatim against this target. Its falsifier
firing closes the card — record and continue the sweep.

**Branch — `web-mass-assignment` also matches**: both classes share the
register-field mechanism. Run the probes once; file the confirmed solve
under the more specific class.

## Phase 2 — baseline the happy path

```bash
for step in register login cart checkout order; do
  curl -i -b "$JAR" ... > baseline_$step.txt
done
```

**Branch — a step fails**: note WHICH step and how. A baseline that
can't complete bounds what the exploit can prove — a flag behind
checkout needs a completing baseline first.

## Phase 3 — the mechanism sweep

Order matters — cheapest and most discriminating first:

1. **mass assignment** — `register`+`role=admin` → read-back.
   - `role: admin` → CONFIRM class → what does admin reach? (phase 4)
   - `role: user` or `400` → falsifier → mechanism dead, next.
2. **workflow skip** — call `/confirm` (or the terminal) bare.
   - `200`+forbidden state → CONFIRM → chain to the flag endpoint.
   - `302/400` to earlier step → falsifier → check WHERE state lives:
     cookie (forgeable), session (harder), or nothing (try the terminal
     endpoint directly — `/flag` may check nothing).
3. **numeric boundary** — the alphabet on `quantity`, then `price`,
   `discount`, `tax`, `amount`.
   - forbidden value accepted into a confirmed state → CONFIRM.
   - `400`/clamp → that field is dead; move to the NEXT FIELD (different
     layer), not the next spelling.
4. **state replay** — the one-time action twice, serially.
   - effect doubles → CONFIRM.
   - `409` → falsifier → the parallel window is race-condition's
     question, not this class's; route if the window matters.
5. **transform check** — `id` at limit, limit+1, word boundaries; diff
   rejection shapes vs malformed.
   - different-layer rejection → CONFIRM the transform runs unchecked →
     compute the wrap target.
   - identical → falsifier → transform checked or absent.

**Branch — everything falsifies**: four+ dead mechanisms = the alphabet
is mostly closed. The remaining surface (unit confusion, trust-in-
earlier-step) needs source or bundle, not more probes. Escalate per
`decide.py` — `novel_plan` or `writeup_search`, not a sixth spelling.

## Phase 4 — chain to the flag

Each confirm opens a new edge. The question after every confirm:
**what does this forbidden state reach?**

- `role: admin` → `/admin`, `/admin/flag`, `/export`, `/users` — GET each.
- `total: -50` → `POST /checkout` — does the charge accept negative?
- double-credit → what does the balance buy? often `/flag` priced above
  the legit max.
- skipped step → the terminal's own read-back: the flag is usually the
  terminal state's payload.

**Branch — the confirm doesn't reach the flag**: the chain needs another
link. Two confirmed flaws compose: mass-assigned role reaching an
endpoint whose own boundary is unvalidated. Composition is the norm in
the verified cards — Pachinko needed the wrap AND the shared memory AND
the appended instructions.

## Phase 5 — flag gate and filing

```bash
python3 tools/hooks.py pre-flag <name> --value "<flag>" \
  --source "the response the flag was read from" --evidence "<flag excerpt>"
python3 tools/classify_solve.py --chain <id>
```

A flag-shaped string outside a live response is a candidate — `pre-flag`
is the gate, not a formality.

## Phase 6 — field notes

Append to `../field-notes.md`: the probe that worked (verbatim), the
falsifiers that fired, the negative that bounded the mechanism. Proposed
entries now; `classify_solve.py` promotes on a verified solve.
