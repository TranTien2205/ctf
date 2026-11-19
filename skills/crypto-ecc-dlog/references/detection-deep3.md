# Detection deep 3 — the reads by constraint shape

## The equality constraints

- `r_i == r_j` → `ecdsa-nonce-reuse` — the strongest single cue.
- `#E == p` → `smart_attack` — the anomalous gate.
- `Δ == 0` → `singular_ec` — the defect gate.
- `h == g^x` → the dlog statement itself.

## The bound constraints

- `k_i < B` → `hnp-ecdsa --nonce-bits/--nonce-bound`.
- `x < B` → `bsgs --order B`.
- `ord(g)` largest factor ≤ 2⁴⁰ → `pohlig-hellman`.
- `ord(g)` ≤ 2⁴⁴ → `bsgs`.

## The count constraints

- `m ≥ required_signatures` → `hnp-ecdsa` viable.
- 1 signature → nothing nonce-shaped.
- `ord` factor count → `pohlig-hellman` CRT width.

## The validation constraints

- `P` validated → invalid curve impossible.
- `P` accepted unvalidated → invalid curve viable.

## The absence constraints

- No `n` → defect intent or count `#E`.
- No `Q` → flag is the proof, not `x·G`.
- No sigs → not nonce family.
