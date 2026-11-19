# Glossary — the terms

## Generator terms

- **LCG** — `x_{i+1} = a·x_i + c mod m`. Params `a` (multiplier), `c`
  (increment), `m` (modulus).
- **LFSR** — linear feedback shift register; a linear recurrence over GF(2)
  defined by **taps** and **width** `w`.
- **MT19937** — Mersenne Twister; 19968-bit state, `temper` per output.
- **xorshift128** — `x ^= x<<13; x ^= x>>17; x ^= x<<5`, 128-bit state.
- **seed** — the generator's initial state; `seed(time())` collapses it.

## The count terms

- **consecutive** — no gap in the output stream's index.
- **raw** — the output as the generator emits it, no transform.
- **truncated** — high bits kept, low `--low-bits` dropped.
- **linear complexity** — the minimal LFSR width BM recovers.
- **624** — the MT full-state window.

## The attack terms

- **`a`, `c`, `m`** — LCG params.
- **`taps`, `width`** — LFSR params (1-indexed-from-LSB convention).
- **`low-bits`** — the DROPPED bits in `lcg-truncated`.
- **`t`, `u`** — not used here (that's `hnp`).
- **`outs`** — comma-separated outputs.
- **`count`** — how many next outputs to emit.

## The evidence terms

- **class evidence** — `predict == held-back` verbatim.
- **impact evidence** — the flag/forged object.
- **falsifier** — `predict != held-back` everywhere.
- **held-back output** — an output not fed to the recovery, used to verify.
