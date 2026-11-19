# Per-check — the measurements that decide each route

## `r`-duplicate check

```python
rs = [s["r"] for s in sigs]
dup = [r for r in rs if rs.count(r) > 1]
```

`dup` non-empty → `ecdsa-nonce-reuse` on the pair.

## `smoothness` check

```bash
python3 tools/crypto_attack.py smoothness --n <ord>
```

Largest factor ≤ 2⁴⁰ → PH; else look elsewhere.

## `Δ` check

```python
delta = (-16 * (4*a**3 + 27*b**2)) % p
delta == 0  → singular_ec
```

## `#E` check

```python
#E = ec.curve(params).order()   # small p only
#E == p  → smart_attack
```

## `required_signatures` check

```python
from tools.crypto import hnp
hnp.required_signatures(order_bits=256, nonce_bits=8)   # e.g. 64
```

`sigs ≥ count` → proceed; else gather more.

## `h ∈ <g>` check

```python
pow(h, order, p) == 1
```

False → `h` in a different subgroup — solve relative to `ord(h)`.

## The verify check

```python
E.mul(G, d) == Q          # curve
pow(g, x, p) == h         # field
```
