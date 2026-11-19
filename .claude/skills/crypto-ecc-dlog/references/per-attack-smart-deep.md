# Per-attack `smart_attack` deep — the card, expanded

## The trigger

A custom curve `y² = x³ + ax + b` over `F_p` with `#E == p` — the anomalous
curve (trace `t = 1`).

## The command

```bash
python3 tools/crypto/smart_attack.py --selftest   # offline check
python3 tools/crypto/smart_attack.py --p P --a A --b B --gx GX --gy GY --qx QX --qy QY --order P
```

A standalone module — `p a b`, the base point `G`, the public `Q`.

## The mechanism

`#E == p` lifts `E` to the `p`-adics `Q_p`; the `p`-adic logarithm is a
homomorphism → the dlog becomes a division.

## The verification

`x·G == Q` via `E.mul` on the original curve.

## The falsifiers

- `#E ≠ p` → not anomalous — `#E` smooth → PH, bounded → bsgs.
- `x·G ≠ Q` → `G`/`Q`/`p` wrong.

## The boundary

- `#E` must be computable — small `p` (else the count itself is the wall).
- `#E` must be EXACTLY `p` — `#E ≈ p` is a normal curve.

## The count check

```python
from tools.crypto import ec
E = ec.curve(...)  # or ec.Curve(p, a, b)
assert E.order() == p   # anomalous gate
```
