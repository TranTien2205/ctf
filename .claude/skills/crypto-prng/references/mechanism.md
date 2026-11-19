# Mechanism — the generators as (F,G) machines

## The model

`state_{i+1}=F(state_i)`, `output_i=G(state_i)`. Invert `G` on enough
outputs → recover `state` → replay `F` → predict.

## The pairs

| Generator | `F` (advance) | `G` (emit) |
|---|---|---|
| LCG | `x←a·x+c mod m` | `x`/`x>>b`/`x mod n` |
| LFSR | shift+xor(taps) | the end bit |
| MT19937 | twist (per 624) | temper (per output) |
| xorshift128 | `x^(x<<11)`/rotate | `w` |
| CSPRNG | stir+entropy | one-way (AES/hash) |

## Why linearity is fatal

`F` linear (GF(2) or mod-m affine) → each output is a linear function of
the state → `S` output bits = `S` equations → solvable. `G` invertible →
the state leaks directly.

## The count floor

`S` state bits / `O` output bits per step = the floor. `624·32=19968` MT,
`4·32=128` xorshift, `2·w` LFSR (taps+state), `3`/`6` LCG (params too).

## The seed entry

`state_0=init(seed)` — a bounded `seed` (`time()`/`pid`) is enumerable
without any output leak.

## The boundary

`G` one-way (CSPRNG) or `key` unknown (keyed cipher) → no output leaks
the state → out of class.
