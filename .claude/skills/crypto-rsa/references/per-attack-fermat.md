# fermat — the close-prime factorisation, complete

## What it is

`n = p·q` with `|p-q|` small → `n = a² - b²` where `a=(p+q)/2` sits just above
`√n`. Walk `a` from `⌈√n⌉` until `a²-n` is a square → `n=(a-b)(a+b)`.

## The mechanism

`a² - n = ((p+q)/2)² - pq = ((p-q)/2)²` — a perfect square `b²` when `a` lands.
The `a` climb is `O(|p-q|/2)` iterations.

## Detection

- **keygen**: `q = next_prime(p)`, `q = p+k`, `q = p+2`, a shared seed, `p`
  generated then `q` derived.
- **the tell**: "primes generated sequentially" / "close primes".

## The bound / falsifier

`|p-q|` small — the `a` walk is `O(|p-q|)`. If `a` walks past the budget, `|p-q|`
is too large → dead; route `pollard-pm1`/a leak.

## The attack

```python
from sympy import integer_nthroot, isqrt
a = isqrt(n) + 1
while True:
    b, ok = integer_nthroot(a*a - n, 2)
    if ok: p, q = a+b, a-b; break
    a += 1
```

Or: `python3 tools/crypto_attack.py fermat --n <n>`.

## The chain

`p`,`q` → `phi` → `d` → `m` → `pow` verify.

## The verify

`p*q==n` proves the split; `pow(m,e,n)==c` proves the plaintext.

## Variants

- **`p+q` leaked** — `p`,`q` from `s=p+q` via the quadratic directly.
- **`n` a square** — `n=p²` → `a=√n` exactly.

## Failure modes

- `|p-q|` large — `a` walks too far → bound it, route elsewhere.
- `n` not `p·q` — a multi-prime or smooth `n`.

## The honest status

Standard published attack (Fermat) — catalogue.
