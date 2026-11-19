# pollard-pm1 — the smooth-predecessor split, complete

## What it is

`p-1` is `B`-smooth (every prime factor ≤ B) → `a^{B!} ≡ 1 mod p` →
`gcd(a^{B!}-1, n) = p` splits `n`.

## The mechanism

`p-1 | B!` → `a^{B!} ≡ 1 mod p` (Fermat's little theorem) → `p | a^{B!}-1` and
`p | n` → `gcd(a^{B!}-1, n) = p`.

## Detection

- **keygen**: `p = getPrime(512)` with `p-1` smooth, `p-1` a product of small
  primes, or a "weak prime" hint.
- **the tell**: `p` generated so `p-1` has small factors.

## The bound / falsifier

`B` ≥ the largest `p-1` factor. `gcd(a^{B!}-1,n)=1` for `B` → `p-1` not smooth
enough → raise `B` or closed.

## The attack

```python
from math import gcd
a = 2
for j in range(2, B+1):
    a = pow(a, j, n)          # a = a^(j) = 2^(j!)
g = gcd(a-1, n)               # >1 → p
```

Or: `crypto_attack.py pollard-pm1 --n <n> --b <B>`.

## The chain

`p` → `q=n/p` → `phi` → `d` → `m` → `pow` verify.

## The verify

`1 < gcd < n` proves a non-trivial factor; `p*q==n` proves the split.

## Variants

- A **stage-2** for one large factor — `pollard-pm1` with a second stage.
- `p+1` smooth → **Williams p+1** (a different method, not this tool).

## Failure modes

- `p-1` not `B`-smooth — `gcd=1`; raise `B` or closed.
- `B` too small — the largest factor missed.

## The honest status

Standard published attack (Pollard 1974) — catalogue.
