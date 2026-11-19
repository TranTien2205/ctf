# common-modulus deep — the shared-modulus Bezout attack, the full treatment

## The mechanism

`c1 = m^e1 mod n`, `c2 = m^e2 mod n`, `gcd(e1,e2)=1`. Bezout's identity gives
`a·e1 + b·e2 = 1` → `m^{a·e1+b·e2} = m^1 = m` → `m = c1^a · c2^b mod n`.

## Detection

- **one `n`, two `e`** (`e1`,`e2`) and two ciphertexts of the same `m`.
- **keygen**: `encrypt(m, e1, n)` and `encrypt(m, e2, n)` — a shared-modulus
  broadcast; a comment like "we reuse n for speed".

## The bound / falsifier

`gcd(e1,e2)=1`. `gcd>1` → recovers `m^gcd`, not `m` — then `nth-root` if
`m^gcd<n`.

## The attack

```python
from sympy import gcdex
g, a, b = gcdex(e1, e2)            # a·e1 + b·e2 = 1
assert g == 1
m = pow(c1, a, n) * pow(c2, b, n) % n
assert pow(m, e1, n) == c1
```

Or: `crypto_attack.py common-modulus --n <n> --e1 <e1> --c1 <c1> --e2 <e2> --c2 <c2>`.

## The chain

`m` → `pow(m,e1,n)==c1` → the flag.

## The verify

`pow(m,e1,n)==c1` — the recovered `m` re-encrypts under `e1`.

## Worked shape

```
e1=3, e2=17, same n, same m
a·3 + b·17 = 1  →  a=-5, b=1?  -15+16=1  →  wait: 5·3-1·17=-2
solve: 6·17 - 34·3 = 0 ... gcdex(3,17) → a, b s.t. a·3+b·17=1
m = c1^a · c2^b mod n
```

## Variants

- `gcd>1` → `m^gcd`; then `small-e`/`nth-root` if `m^gcd<n`.
- >2 exponents — Bezout generalises pairwise (chain two at a time).
- the same `n` with a *private* `d` for one `e` → `rsa-decrypt` directly.

## Failure modes

- `gcd>1` — `m^gcd`, not `m`.
- different `m` per ciphertext — the relation isn't shared-`m`.
- `pow(c1,a,n)` with negative `a` — Python computes the modular inverse.

## The honest status

Standard published attack — catalogue.
