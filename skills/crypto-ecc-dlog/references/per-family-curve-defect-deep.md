# Per-family curve-defect deep — the defect family, expanded

## The three attacks

| Attack | Trigger | Files |
|---|---|---|
| `smart_attack` | `#E == p` (trace 1) | `per-attack-smart.md`,`smart-attack-deep.md` |
| `singular_ec` | `Δ == 0` | `per-attack-singular.md`,`singular-ec-deep.md` |
| invalid curve | unvalidated `P` oracle | `per-attack-invalid-curve.md`,`invalid-curve-deep.md` |

## The defect ladder — the order matters

```
Δ == 0?       → singular_ec     (the most degenerate)
#E == p?      → smart_attack    (anomalous)
#E smooth?    → pohlig-hellman (curve ops via ec.py)
unvalidated?  → invalid curve   (the oracle variant)
else          → generic dlog / re-read
```

`Δ` first, `#E` next, smoothness next, validation last — cheapest to
check, most specific to exploit.

## The `ec.py` machinery

- `E.mul(P, k)` — curve ops for `bsgs`/`pohlig` on the curve and for the
  fake-curve oracle responses.
- `E.point(x, y)` / `E.curve`/`E.order()` — construction and counting.

## The verify

`x·G == Q`/`d·G == Q` on the ORIGINAL curve — a scalar that verifies on a
fake `E'` is not the key.
