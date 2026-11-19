# Troubleshoot — the fixes

## `lcg-recover` fails

- `x1-x0` not invertible → `gcd(x1-x0, m) > 1` → factor `m` or gather
  outputs.
- `predict != held-back` → `m` wrong, not LCG, or outputs not consecutive.

## `lcg-unknown-modulus` fails

- `gcd` returns 1 or a huge multiple → not raw LCG / outputs processed.
- <6 outputs → gather more.

## `lcg-truncated` fails

- lattice junk → `required` count not met → more outputs.
- `predict != held-back` → `--low-bits`/`m`/`a`/`c` wrong.
- the leak is `x mod 2^k` not `x >> b` → different shape.

## `berlekamp-massey` fails

- complexity ≈ stream length → not an LFSR (combiner? other cipher?).
- <2·w bits → more bits.
- wrong taps → `--keystream-hex` vs `--bits` packing.

## `lfsr-recover`/`lfsr-predict` fails

- `predict != held-back` → `taps`/`width` convention or alignment.
- `lfsr-predict` diverges at bit `w` → `taps` wrong.

## `mt19937-clone` fails

- <624 → can't clone — need the full window or a different approach.
- `predict != held-back` → floats/randint/reseed — not raw words.

## `xorshift128` fails

- `predict != held-back` → `128+`/`64*`/`xorwow` variant, not xorshift128.

## seed-search fails

- unbounded window → bound the epoch from the challenge.
- `predict != held-back` → wrong seed model (pid+time, int-vs-float time).
