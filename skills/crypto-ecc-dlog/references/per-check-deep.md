# Per-check deep — the measurements, annotated

## `r`-dedupe — the check

```python
from collections import Counter
dups = [r for r, c in Counter(s["r"] for s in sigs).items() if c > 1]
```

`dups` non-empty → `ecdsa-nonce-reuse` on the pair. The check is `O(n)`,
free, and decides the whole branch.

## `smoothness` — the check

```bash
python3 tools/crypto_attack.py smoothness --n <ord>
```

Returns factors + largest factor. `≤2⁴⁰` largest → `pohlig-hellman`;
`2⁴⁰..2⁴⁴` → PH slow, `bsgs` maybe; `>2⁴⁴` → neither — defect or protocol.

## `Δ` — the check

```python
delta = (-16 * (4 * a**3 + 27 * b**2)) % p
delta == 0  # → singular_ec
```

Exact zero required — near-zero means a normal curve.

## `#E` — the check

```python
E = ec.curve({"p": p, "a": a, "b": b})
n_points = E.order()       # feasible on small p
n_points == p              # → smart_attack
```

`#E` smooth → `pohlig-hellman` with `ec.py` point ops.

## `required_signatures` — the check

```python
from tools.crypto import hnp
hnp.required_signatures(order_bits=256, nonce_bits=128)   # ~4
```

`len(sigs) < count` → gather more; `≥` → proceed.

## `h ∈ <g>` — the check

```python
pow(h, order, p) == 1   # h in <g>
```

False → `h` lives in another subgroup — solve relative to `ord(h)` instead.

## The verify — the check

```python
E.mul(E.point(*G), d) == E.point(*Q)   # curve
pow(g, x, p) == h                    # field
```
