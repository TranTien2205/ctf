# Detection playbook — the six-step procedure

## Step 0 — inventory

What does the handout actually contain? Curve params, sig pairs, dlog
statement, service endpoint, custom curve. Write it down.

## Step 1 — name the group

Curve name → `n`, `G`, `p`, `a`, `b`. `h = g^x mod p` → `p`, `g`, `ord(g)`.
Named curve (secp256k1, P-256) → nonce attacks, not curve defects.

## Step 2 — signatures?

- `r` equal across two → `ecdsa-nonce-reuse`.
- `r` distinct, `k` hinted bounded → `hnp-ecdsa` (count via
  `required_signatures`).
- Partial `k` leaked → `hnp`.

## Step 3 — dlog?

- `smoothness --n <ord>` → `pohlig-hellman` if smooth.
- `x` bounded → `bsgs`.
- Else → re-read for a defect.

## Step 4 — defect?

- `Δ == 0` → `singular_ec`.
- `#E == p` → `smart_attack`.
- server unvalidated → invalid curve.

## Step 5 — verify + record

`x·G == Q`/`g^x == h` → `post-probe` → `../field-notes.md` → `decide.py` if stuck.

## The route files

`detection*.md`, `cipher-identification.md`, `detection-matrix.md`,
`per-family-*.md`.
