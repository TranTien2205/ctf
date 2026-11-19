# Falsifiers — the kill conditions

## The universal falsifier

`predict_next != held-back` — a generator whose next value you cannot
produce exactly is not recovered. Every attack shares it.

## `lcg-recover`

- `x1-x0` not invertible mod `m` → more outputs / factor `m`.
- `predict != held-back` → wrong `m`, not LCG, or not consecutive.

## `lcg-unknown-modulus`

- gcd of the telescoping terms = 1 or non-`m` → not a raw LCG.
- <6 outputs → the gcd isn't pinned.

## `lcg-truncated`

- `m`,`a`,`c` not all known → no lattice to build.
- kept bits too few → no short vector.
- `predict != held-back` → `--low-bits` or shape wrong.

## `berlekamp-massey` / `lfsr-*`

- linear complexity ≈ stream length → not an LFSR.
- <2·w bits → underdetermined.
- predicted bits diverge → taps/width/convention wrong.

## `mt19937-clone`

- <624 words → state underdetermined — NO clone.
- `predict != held-back` → not raw `getrandbits(32)`, or a reseed.

## `xorshift128`

- <4 outputs → underdetermined.
- `predict != held-back` → wrong xorshift variant.

## seed-search

- unbounded window / CSPRNG seed → not enumerable → wrong class.

## The class falsifier

`predict != held-back` everywhere → the source is a CSPRNG or keyed — NOT
a predictable generator → `class-boundary.md`.
