# Workflow deep — the full decision walkthrough

## Phase 0 — the inventory

Write down: what the handout has (sigs/params/oracle/dlog), the group
(curve name or `p,a,b,G,n`), and the deliverable (a `d`, an `x`, a `k`).

## Phase 1 — signature branch

- `len(sigs) < 2` → dead end on nonce alone; look at the oracle or the curve.
- any `r_i == r_j` → `ecdsa-nonce-reuse` on the pair.
- all `r` distinct + a nonce bound → `hnp-ecdsa`.
- partial `k` per sig → `hnp`/`hnp-ecdsa` with the correct `B`.

## Phase 2 — dlog branch

- `smoothness --n <ord>` → if largest factor ≤ 2⁴⁰ → `pohlig-hellman`.
- `x < B` stated → `bsgs` with `--order B`.
- `ord` small → `bsgs`.

## Phase 3 — defect branch

- `Δ ≡ 0` → `singular_ec`.
- `#E == p` → `smart_attack`.
- server multiplies unvalidated points → invalid curve (ec.py + per-curve
  bsgs + CRT).

## Phase 4 — solve

`payload-dictionary.md` / `payload-dictionary-deep.md` — the exact commands.
Prepare `--sigs` JSON; `--order` is always `n`.

## Phase 5 — verify

`x·G == Q` / `g^x == h` — a fail means wrong attack/wrong input, not "almost".

## Phase 6 — close

`post-probe` → `../field-notes.md` → `classify_solve.py` on a solve, or
`knowledge/attempts/` falsifier on a dead end → `decide.py` for the next step.

## The honest status

Every attack is a candidate-generator; verify is the proof.
