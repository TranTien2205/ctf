# per-attack wiener deep — the small-d continued-fraction, the full treatment

## The mechanism

`ed ≡ 1 mod φ` → `ed - k·φ = 1`, `k < d`. Dividing by `d·n`, `φ ≈ n` →
`|e/n - k/d| < 1/(3d²)` when `d < (1/3)·n^0.25`. `k/d` is a convergent of the
CF of `e/n` — enumerate, get `phi' = (e·d-1)/k`, solve `x²-(n-phi'+1)x+n=0`.

## Detection

- **`e`≈`n`** — `e = inverse(d,phi)` for small `d` ≈ `n`.
- **keygen**: `d` explicitly small.

## The bound / falsifier

`d < n^0.25`. `d ≥ n^0.25` → `boneh-durfee` (`n^0.292`); `d ≥ n^0.292` → closed.

## The attack

```bash
crypto_attack.py wiener --n <n> --e <e>
```

```python
for (k,d) in convergents(e/n):
    if (e*d-1) % k == 0:
        phi = (e*d-1)//k
        s = n - phi + 1; disc = s*s - 4*n
        if is_square(disc): return d, (s+isqrt(disc))//2, (s-isqrt(disc))//2
```

## The verify

`pow(c,d,n)==m`, `pow(m,e,n)==c`, `p*q==n`.

## Variants

- `d` just over `n^0.25` → `boneh-durfee`.
- The CF misses → `boneh-durfee-escalate`.

## Failure modes

- `d ≥ n^0.25` — Wiener's bound.
- `e` not large — `d` is ~`n`, not small.

## The honest status

Wiener 1990 — catalogue.
