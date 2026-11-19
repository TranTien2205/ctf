# Evasion deep — the disguises in full

## The nonce disguises

- **`k_i = base + i·step`** — structured nonces, distinct `r` — `hnp-ecdsa`
  with `--nonce-bound` covering the step range.
- **`k = PRNG(m)`** — deterministic per message, differs across — gather
  ~count sigs; if the PRNG is weak (`mt19937`/`lcg`), that's `crypto-prng`.
- **High bits fixed, low random** — `k = hi·2^L + low`, `low < 2^L` →
  `hnp` with `B = 2^L`.

## The order disguises

- `ord(g)` factors hidden — `p-1` given as `p-1 = 2·Π q_i` in the handout,
  or `g` in a small subgroup → `ord(g)`, not `p-1`.
- `#E` withheld → count or check defect intent.

## The curve disguises

- `b = 0` or `a = 0` — still a curve, `Δ` check applies.
- Params in hex strings vs ints — normalize before `Δ`/`ec.curve`.
- `G`/`Q` compressed — decompress first.

## The message disguises

- `z` given as hex string — `--sigs` accepts it; ensure the *value* is the
  truncated hash.
- `z` on the raw message — hash it (`sha256 → int`).

## The flag disguises

- The recovered `x`/`d` feeds a decrypt or a JWT forge — `flag{…}` sits at
  the *end* of the chain, not inside the scalar.

## The verify disguise

A `d` verifying on a *different* curve means the handout's `Q` was for
another curve — re-check which `G`/`p`/`a`/`b` the supplied `Q` uses.
