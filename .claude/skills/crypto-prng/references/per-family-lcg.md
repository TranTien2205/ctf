# Per-family LCG — the linear congruential branch

## The three attacks

| Attack | Trigger | Card |
|---|---|---|
| `lcg-recover` | `m` known, ≥3 outs | `per-attack-lcg-recover.md` |
| `lcg-unknown-modulus` | `m` unknown, ≥6 outs | `per-attack-lcg-unknown-modulus.md` |
| `lcg-truncated` | high bits only, `m`,`a`,`c` known | `per-attack-lcg-truncated.md` |

## The discriminator

```
m known?       → lcg-recover (>=3 outs)
m unknown?     → lcg-unknown-modulus (>=6 outs)
truncated?     → lcg-truncated (high bits, m/a/c known, --low-bits)
```

## The invariants

- `--outputs` is comma-separated ints (or `--in` JSON).
- `--modulus` is `m`, `--a`/`--c` the params, `--low-bits` the DROPPED bits.
- Consecutive + raw — a `mod`/`hex`/`float` between state and observation
  breaks the affine structure.

## The fingerprint

Unknown generator → the diff/gcd fingerprint: `x_{i+1} - x_i` and the
telescoping products `t_{i+1}·t_{i-1} - t_i²` share `m` as a divisor.

## The verify

`predict_next == held-back` — a state that doesn't reproduce the next
output isn't recovered.

## The boundary

`m` composite with a shared factor in `x1-x0` → the inverse for `a` doesn't
exist → factor `m` or gather more outputs.
