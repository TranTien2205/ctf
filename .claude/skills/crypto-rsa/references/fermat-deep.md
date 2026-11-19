# fermat deep — the close-prime factorisation, the full treatment

## The mechanism

`n = p·q` with `|p-q|` small → `n = a² - b²` where `a=(p+q)/2` sits just above
`√n`. `a² - n = ((p+q)/2)² - pq = ((p-q)/2)²` — a perfect square `b²` when `a`
lands. Walk `a` from `⌈√n⌉` until `a²-n` is a square → `n=(a-b)(a+b)`.

## Detection

- **keygen**: `q = next_prime(p)`, `q = p+k`, `q = p+2`, a shared seed, `p`
  generated then `q` derived.
- **the tell**: "primes generated sequentially" / "close primes" / a comment
  about `next_prime`.

## The bound / falsifier

`|p-q|` small — the `a` walk is `O(|p-q|)`. If `a` walks past the budget,
`|p-q|` is too large → dead; route `pollard-pm1`/a leak.

## The attack

```python
from sympy import integer_nthroot, isqrt
a = isqrt(n) + 1
for _ in range(10_000_000):      # bound the climb
    b, ok = integer_nthroot(a*a - n, 2)
    if ok:
        p, q = a+b, a-b
        break
    a += 1
```

Or: `python3 tools/crypto_attack.py fermat --n <n> --max-iters <K>`.

## The chain

`p`,`q` → `phi` → `d` → `m` → `pow` verify.

## The verify

`p*q==n` proves the split; `pow(m,e,n)==c` proves the plaintext.

## Worked shape

```
n = p·q, p ≈ q
a = (p+q)/2, b = (p-q)/2,  a² - b² = pq = n
# a is just above √n — walk it
```

## Variants

- **`p+q` leaked** — `p`,`q` from `s=p+q` via the quadratic directly.
- **`n` a square** — `n=p²` → `a=√n` exactly, `phi=p(p-1)`.
- **a "close but not adjacent" `p`,`q`** — a few thousand iterations.

## Failure modes

- `|p-q|` large — `a` walks too far → bound it (`--max-iters`), route elsewhere.
- `n` not `p·q` — a multi-prime or smooth `n` → a different `phi`.

## The honest status

Fermat's method — catalogue.
