# Smart's attack — anomalous curves (`#E(Fp) == p`)

## When it applies

A custom curve `y² = x³ + ax + b over Fp` where the point count equals the
field: `#E(Fp) = p`. Called an *anomalous curve* — completely broken by
Smart's p-adic lift in linear time.

## Detection

1. Handout gives `p, a, b` — a custom curve.
2. Count points: `#E = p + 1 - t`, trace `t`. If the handout gives `#E`,
  compare with `p` — equal → anomalous.
3. If `#E` isn't given, `tools/crypto/ec.py` can count on small fields;
  for larger ones the challenge usually supplies it.

## The tool

```bash
python3 tools/crypto/smart_attack.py --selftest   # proves the module
```

In code — the module solves `Q = x·P` directly on the anomalous curve:

```python
from tools.crypto import smart_attack
# smart_attack solves the ECDLP on E(Fp) when #E(Fp) == p via a p-adic lift
```

## The math (sketch)

Lift `E` and the points `P, Q` to `E(Q_p)`. The p-adic elliptic logarithm of
`x·P'` and `Q'` both land in `p·Q_p`; their ratio is `x mod p`. Two
divisions, no search — `O(log p)` total.

## Preconditions

- `p` prime, curve nonsingular over `Fp` (singular → `singular_ec` instead).
- `#E(Fp) == p` exactly — `p±1`, `p+2` don't qualify.

## Falsifier

`x·G ≠ Q` after the attack → the curve wasn't anomalous (recheck the count),
or points were given in a different curve. If `#E` isn't `p`, move on —
`pohlig-hellman` (smooth `#E`), `singular_ec`, or `bsgs`.

## Common mistakes

- Counting `#E` on the wrong field — it must be over `Fp`, not an extension.
- Confusing "prime order" (good) with "order = p" (anomalous, broken).
- Trying Smart's on `secp256k1` — `#E ≈ p` but not equal; it fails.
