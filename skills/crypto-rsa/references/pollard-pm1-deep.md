# pollard-pm1 deep — the smooth predecessor

## The precondition

`n` has a factor `p` where `p-1` is **B-smooth** — all its prime factors ≤ `B`.
Hint: "weak prime", a `p-1`-construction in the keygen, or `n` resisting every
cheap attack.

## The maths

By Fermat's little theorem, `a^(p-1) ≡ 1 mod p`. If `p-1` divides `M` (e.g.
`M = B!` or `M = lcm(1..B)`), then `a^M ≡ 1 mod p` → `p | a^M - 1` →
`gcd(a^M - 1, n) = p`.

The incremental form: `a ← a^k mod n` for `k=2,3,…,B` computes `a^(B!)` without
the huge `M` — `a_k = a_(k-1)^k`.

```python
from math import gcd
a = 2
for k in range(2, B+1):
    a = pow(a, k, n)          # a = 2^(k!) mod n
g = gcd(a-1, n)
if 1 < g < n: p = g
```

## The tool

```bash
python3 tools/crypto_attack.py pollard-pm1 --n <n> --e <e> --c <c>
```

## The bound / falsifier

`B` must be ≥ the largest prime factor of `p-1`. `gcd=1` for a reasonable `B`
(~10⁵–10⁶) → `p-1` not smooth enough → negative.

## The verify

`gcd=p` with `1<p<n`; `p*q==n`; `rsa-decrypt` → `pow(m,e,n)==c`.

## The traps

- `gcd=n` if `q-1` is *also* `B`-smooth → retry with a smaller `B` or another `a`.
- `p+1` smooth → Williams `p+1`, a different method — `pollard-pm1` is `p-1` only.
- A moderate `B` is cheap; a huge `B` is brute-force — pick `B` from the hint.

## Why "weak prime" is the tell

The challenge telegraphs it: `p` built as `prod(small_primes)+1`, or a comment
about a "smooth" or "weak" prime. The `p-1` construction is the attack's whole
precondition.
