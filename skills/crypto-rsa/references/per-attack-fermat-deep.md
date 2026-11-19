# per-attack fermat deep — the close-prime split, the full treatment

## The mechanism

`n = p·q`, `|p-q|` small → `n = a² - b²`, `a=(p+q)/2` just above `√n`,
`b=(p-q)/2`. Walk `a` from `⌈√n⌉` until `a²-n` is square → `n=(a-b)(a+b)`.

## Detection

- **keygen**: `q=next_prime(p)`, `q=p+k`, `q=p+2`, shared seed, `p` then `q`.
- **tell**: "primes sequentially"/"close".

## The bound / falsifier

`|p-q|` small — the `a` walk `O(|p-q|)`. Past `--max-iters` → dead → `pollard-pm1`/leak.

## The attack

```bash
crypto_attack.py fermat --n <n> --max-iters <K>
```

```python
from sympy import integer_nthroot, isqrt
a = isqrt(n) + 1
for _ in range(10**7):
    b, ok = integer_nthroot(a*a-n, 2)
    if ok: p,q = a+b, a-b; break
    a += 1
```

## The verify

`p*q==n` → `phi` → `d` → `m` → `pow`.

## Variants

- `p+q` leaked → quadratic directly.
- `n`=p² → `a=√n` exactly, `phi=p(p-1)`.

## Failure modes

- `|p-q|` large → the budget passed → dead.
- `n` not `p·q` → multi-prime/smooth → a different `phi`.

## The honest status

Fermat — catalogue.
