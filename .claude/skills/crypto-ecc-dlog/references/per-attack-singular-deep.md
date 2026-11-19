# Per-attack `singular_ec` deep — the card, expanded

## The trigger

`Δ = 4a³ + 27b² ≡ 0 (mod p)` — the cubic has a node or cusp.

## The command

```bash
python3 tools/crypto/singular_ec.py --selftest   # offline check
python3 tools/crypto/singular_ec.py --p P --a2 0 --a1 A --a0 B --gx GX --gy GY --qx QX --qy QY
```

A standalone module — `P`, `Q` must be the nonsingular points.

## The mechanism

- Node → `E ≅ G_m` → field dlog (`bsgs`/`pohlig` on `F_p*`).
- Cusp → `E ≅ G_a` → additive — the dlog is a division.

## The verification

`x·G == Q` on the original (singular) curve.

## The falsifiers

- `Δ ≠ 0` → not singular.
- `P`/`Q` at the singular point → the iso doesn't apply.

## The boundary

- `Δ` must be EXACTLY `0 mod p` — near-zero is a normal curve.
- The singular point is excluded — points there don't map cleanly.

## The `Δ` check

```python
Delta = (4*a**3 + 27*b**2) % p
assert Delta == 0   # singular gate
```
