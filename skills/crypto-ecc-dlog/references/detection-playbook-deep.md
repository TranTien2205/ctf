# Detection playbook deep — every step with the underlying check

## Step 0 — the artifact inventory

What exists: a `sigs` collection, curve params, a `h = g^x` statement, a
signing/multiply oracle, or a combination.

## Step 1 — the cheap reads (free)

- **`r` dedupe** — the single most common CTF shape.
- **`Δ mod p`** — `4a³ + 27b² mod p` — seconds.
- **`#E == p`** — count compare if `#E` given.
- **`required_signatures`** — do you even have enough for HNP.

## Step 2 — the smoothness gate (seconds)

`smoothness --n <ord>` — factoring `ord`/`p-1`/`#E` tells you PH feasibility.
Not optional for dlog shapes.

## Step 3 — the bound read

What does the challenge *say* about `k` or `x`?

- "128-bit nonce" → `--nonce-bits 128`.
- "timestamp k" → `--nonce-bound <ts_max>`.
- "small exponent" → `bsgs --order <bound>`.

## Step 4 — the oracle probes

- `sign(m)` ×2 → determinism.
- `multiply(P')` with off-curve `P'` → validation presence.

## Step 5 — the solve

`payload-dictionary*.md` — the exact command for the chosen attack.

## Step 6 — the verify

`x·G == Q`/`pow(g, x, p) == h` — the finish line.

## Step 7 — the close

`post-probe` → `../field-notes.md` → `classify_solve.py` / `attempts` → `decide.py`.
