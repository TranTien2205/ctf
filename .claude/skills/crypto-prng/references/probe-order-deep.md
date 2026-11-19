# Probe order deep — cheapest measurement first, always

## The principle

Spend the cheapest measurement first — it either routes the solve or
kills the hypothesis at minimum cost. The count and normalization gates
cost nothing; the lattice/clone cost the most.

## The order — annotated

### 1. parse — free

Extract outputs. Buy the stream — no inference yet.

### 2. shape — free

int/hex/float/bit/`mod n`/`>>b` — the family hint, free.

### 3. name — free

grep the generator name — the highest-power fingerprint, free.

### 4. count — free

`len(outputs)` vs the floor — kills `<624` MT / `<6` unknown-mod / `<4`
xorshift instantly.

### 5. fingerprint — cheap

- `gcd` on ints — O(n) — LCG or not.
- `berlekamp-massey` on bits — O(L²) — LFSR or not.
- 624-clone test — O(624) — MT or not.

### 6. params — cheap

`m`/`a`,`c`/taps/`low-bits`/seed-window from source — picks the specific
attack.

### 7. attack — the cost

- `lcg-recover` — one inverse, closed form, cheapest.
- `lcg-unknown-modulus` — a gcd, cheap.
- `lfsr-predict` — linear roll, cheap.
- `berlekamp-massey` — O(L²), moderate.
- `lcg-truncated` — a lattice, heaviest.
- `mt19937-clone` — 624 untempers, cheap once you have the outputs.
- `xorshift128` — a 128-bit linear solve, cheap.
- seed-search — `window` clones — bounded.

### 8. verify — free

`predict == held-back` — always last, always cheap.

## The skip rule

Never run step 7 before steps 1-6 pass. A 623-output `mt19937-clone` is
a guaranteed-zero — the count gate (step 4) kills it for free.

## The falsifier-first rule

The cheapest falsifier kills first. `predict != held` on a single
held-back output is cheaper than a second recovery attempt — run it
before re-attacking.
