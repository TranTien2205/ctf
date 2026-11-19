# fermat deep — the close-prime factorisation

## The precondition

`p` and `q` generated close together: `q = next_prime(p)`, `q = p + 2`, `q = p +
k` for small `k`, or a shared seed producing nearby primes.

## The maths

`n = p·q`. If `p ≈ q`, write `p = a+b`, `q = a-b` for `a = (p+q)/2`, `b =
(p-q)/2`. Then `n = a² - b²`, so `a² - n = b²` — a perfect square. `a ≈ √n`
since `p ≈ q` makes `(p+q)/2 ≈ √n`.

## The procedure

```python
from sympy import isqrt, integer_nthroot
a = isqrt(n)
if a*a < n: a += 1          # ceil, not floor
while True:
    b2 = a*a - n
    b, is_sq = integer_nthroot(b2, 2)
    if is_sq:
        p, q = a+b, a-b
        assert p*q == n
        break
    a += 1
```

Converges in `O(|p-q|)` iterations — instant for `next_prime`, too slow for
balanced random primes.

## The tool

```bash
python3 tools/crypto_attack.py fermat --n <n> --e <e> --c <c>
```

## The bound / falsifier

The gap `|p-q|` must be small. Balanced independent primes have `|p-q| ~ √n` →
`a` climbs ~√n steps — infeasible → negative. The tell is in the **keygen**, not
the modulus.

## The verify

`p*q==n`, `d = inverse(e,(p-1)(q-1))`, `pow(c,d,n)==m`.

## The traps

- **Bit-length balance ≠ value closeness.** `p`,`q` both 512-bit is standard
  safe RSA. Fermat needs the numeric gap small — `next_prime`, `p+2`, a seed.
- `a` must be `ceil(√n)`, not `floor` — a floor `a` starts below and misses.
- A "the primes are close" comment is the direct tell; run Fermat first.
- If the gap is `~2` (twin primes), Fermat converges in ~1 step.
