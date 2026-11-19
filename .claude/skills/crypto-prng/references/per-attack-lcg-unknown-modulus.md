# Per-attack `lcg-unknown-modulus` — the card

## Trigger

LCG with `m` UNKNOWN — you hold ≥6 consecutive outputs and the modulus is
not given.

## Command

```bash
python3 tools/crypto_attack.py lcg-unknown-modulus --outputs x0,x1,x2,x3,x4,x5
```

## Mechanism

```
t_i = x_{i+1} - x_i
m | (t_{i+1}·t_{i-1} - t_i^2)   →   m = gcd of several such terms
```

Once `m` is recovered → `lcg-recover` for `a`,`c`.

## Verify

`m` recovered → `a`,`c` → `predict == held-back`.

## Falsifiers

- <6 outputs → the gcd can't be trusted — need more.
- `gcd` yields 1 or a non-integer → not a raw LCG / outputs not
  consecutive.
- `predict != held-back` → not an LCG.

## Boundaries

- The gcd trick needs enough terms that the true `m` is the only common
  divisor — 6 is the floor, more is safer.
- If the gcd gives a multiple of `m`, `lcg-recover` may still work — or
  factor the gcd.
- Truncated outputs → this is `lcg-truncated`, not unknown-modulus.
