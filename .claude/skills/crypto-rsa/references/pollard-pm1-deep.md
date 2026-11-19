# pollard-pm1 deep — the smooth-predecessor split, the full treatment

## The mechanism

If `p-1` is `B`-smooth (every prime factor ≤ B), then `p-1 | B!` → `a^{B!} ≡ 1
mod p` by Fermat's little theorem → `p | a^{B!}-1` and `p | n` →
`gcd(a^{B!}-1, n) = p`.

## Detection

- **keygen**: `p = getPrime(512)` where `p-1` is smooth, a product of small
  primes, or a "weak prime" / "smooth predecessor" hint.
- **the tell**: `p` generated so `p-1` has small factors — or `p` reused.

## The bound / falsifier

`B` ≥ the largest `p-1` factor. `gcd(a^{B!}-1,n)=1` for `B` → `p-1` not smooth
enough → raise `B` or closed.

## The attack

```python
from math import gcd
a = 2
for j in range(2, B+1):
    a = pow(a, j, n)          # a = a^(j) accumulates 2^(j!)
g = gcd(a-1, n)               # >1 → p
```

Or: `crypto_attack.py pollard-pm1 --n <n> --b <B>`.

## The chain

`p` → `q=n/p` → `phi` → `d` → `m` → `pow` verify.

## The verify

`1 < gcd < n` proves a non-trivial factor; `p*q==n` proves the split.

## Worked shape

```
n = p·q, p-1 = product of primes ≤ B
a = 2^(B!) mod n   →   a ≡ 1 mod p   →   gcd(a-1, n) = p
```

## Variants

- A **stage-2** for one large factor — `pollard-pm1` with a second stage
  (`a^{B!}·a^{j}` for primes `j>B`).
- `p+1` smooth → **Williams p+1** (a different method, not this tool).
- `p-1` *and* `p+1` both smooth → either method splits it.

## Failure modes

- `p-1` not `B`-smooth — `gcd=1`; raise `B` or closed.
- `B` too small — the largest factor missed → raise `B`.

## The honest status

Pollard 1974 — catalogue.
