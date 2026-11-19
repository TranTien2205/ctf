# First hour deep — the 0→60-minute plan with the why

## 0–5 min — the inventory

Write the group: `p a b G Q n` or the named curve. Count sigs, dedupe `r`,
pick the `z` convention (FIPS truncation). Probe the oracle once
(determinism/validation).

## 5–10 min — the gates (all free)

- `r` dup? → reuse.
- `smoothness --n ord` → PH feasibility.
- `Δ`/`#E` → defect.
- `required_signatures` → enough sigs?
- Validation? → invalid curve.

## 10–25 min — the solve

`payload-dictionary*` — the exact command for the chosen attack. Prepare
`--sigs` JSON carefully (most errors are format). For lattice attacks,
`--curve`/`--pubkey` self-verify saves a step.

## 25–30 min — verify

`x·G == Q`/`pow(g, x, p) == h` — non-negotiable. Then the flag step:
decrypt or forge → `flag{…}`.

## 30–45 min — record

`post-probe` with verbatim output → `../field-notes.md` → `classify_solve.py`
on solve / `knowledge/attempts/` on dead end.

## 45–60 min — the stuck path

`troubleshoot*.md` for the failure class → `falsifiers*.md` for the kill
condition → `decide.py` for the next rung (`chain_match` → `reclassify` →
`writeup_search` → `novel_plan` → `fanout_sweep` → `solver_handoff`).

## The budget reality

5 probes / 15 min per mechanism, 25 / 45 total — the controller enforces
it; a spent budget is strategy change, not end-of-challenge.
