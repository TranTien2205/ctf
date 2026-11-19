# wiener — the small-d continued-fraction attack, complete

## What it is

When `d < n^0.25`, `k/d` is a convergent of `e/n` — the continued-fraction
expansion of `e/n` recovers `d` directly.

## The mechanism

`ed ≡ 1 mod φ` → `ed - k·φ = 1`. With `φ ≈ n` and `d < n^0.25`:
`|e/n - k/d| < 1/(3d²)` → `k/d` is a convergent of `e/n`.

## Detection

- **`e` ≈ `n` in bit-length** — `e=inverse(d,phi)` for small `d` ≈ `n`.
- **keygen**: `d = getPrime(small)` or `d` derived small.
- **the tell**: a "fast decryption" note → small `d`.

## The bound / falsifier

`d < n^0.25`. `d ≥ n^0.25` → `wiener` returns nothing → escalate to
`boneh-durfee` (`n^0.292`). `d ≥ n^0.292` → small-d closed.

## The attack

```python
# convergents k_i/d_i of e/n; for each:
#   phi' = (e*d_i - 1) / k_i
#   solve x² - (n - phi' + 1)x + n = 0 → if integer roots, d_i is d
```

Or: `python3 tools/crypto_attack.py wiener --n <n> --e <e>`.

## The chain

`d` → `m = c^d mod n` → `pow(m,e,n)==c`.

## The verify

`pow(c,d,n)==m` recovers the plaintext; `pow(m,e,n)==c` proves it.

## Variants

- **`d` just over `n^0.25`** → `boneh-durfee` (the wider bound).
- **CF too slow / misses** → `boneh-durfee-escalate` (`m`,`t` up).

## Failure modes

- `d ≥ n^0.25` — Wiener's bound; `boneh-durfee` reaches `n^0.292`.
- `e` not large — if `e`≈65537, `d` is ~`n` → not small-d.

## The honest status

Standard published attack (Wiener 1990) — catalogue.
