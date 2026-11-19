# common-modulus — the shared-modulus Bezout attack, complete

## What it is

`c1 = m^e1 mod n`, `c2 = m^e2 mod n`, `gcd(e1,e2)=1` — Bezout `a·e1+b·e2=1` →
`m = c1^a · c2^b mod n`.

## The mechanism

`m^{a·e1+b·e2} = m^1 = m` → `c1^a · c2^b = m^{a·e1}·m^{b·e2} = m^{a·e1+b·e2} = m`.

## Detection

- **one `n`, two `e`** (`e1`,`e2`) and two ciphertexts of the same `m`.
- **keygen**: `encrypt(m, e1, n)` and `encrypt(m, e2, n)` — a shared-modulus
  broadcast.

## The bound / falsifier

`gcd(e1,e2)=1`. `gcd>1` → recovers `m^gcd`, not `m` — then `nth-root` if
`m^gcd<n`.

## The attack

```python
from sympy import gcdex
g, a, b = gcdex(e1, e2)          # a·e1 + b·e2 = 1
m = pow(c1, a, n) * pow(c2, b, n) % n
assert pow(m, e1, n) == c1
```

Or: `crypto_attack.py common-modulus --n <n> --e1 <e1> --e2 <e2> --c1 <c1> --c2 <c2>`.

## The verify

`pow(m,e1,n)==c1` — the recovered `m` re-encrypts.

## Variants

- `gcd>1` → `m^gcd`; then `small-e`/`nth-root` if `m^gcd<n`.
- >2 exponents — Bezout generalises pairwise.

## Failure modes

- `gcd>1` — `m^gcd`, not `m`.
- different `m` per ciphertext — the relation isn't shared-`m`.

## The honest status

Standard published attack — catalogue.
