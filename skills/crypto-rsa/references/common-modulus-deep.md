# common-modulus deep — Bezout on coprime exponents

## The precondition

One modulus `n` shared by two public exponents `e1`, `e2`; the **same** message
`m` encrypted to both: `c1 = m^e1 mod n`, `c2 = m^e2 mod n`. The classic "same
secret to two recipients who share a modulus."

## The maths

`gcd(e1,e2)=1` ⇒ extended Euclidean gives `a`,`b` with `a·e1+b·e2=1`. Then

```
c1^a · c2^b = m^(a·e1) · m^(b·e2) = m^(a·e1 + b·e2) = m^1 = m   (mod n)
```

One of `a`,`b` is negative — `c^(-k) mod n` = `pow(c, -1, n)^k` = `pow(c, -k, n)`.

## The procedure

```python
from math import gcd
def egcd(a,b):
    if b==0: return (a,1,0)
    g,x,y=egcd(b,a%b); return (g, y, x-(a//b)*y)
g,a,b = egcd(e1,e2)
assert g==1
m = (pow(c1,a,n)*pow(c2,b,n))%n
```

## The tool

```bash
python3 tools/crypto_attack.py common-modulus --n <n> --e1 <e1> --e2 <e2> --c1 <c1> --c2 <c2>
```

## The bound / falsifier

`gcd(e1,e2)=1` is required. `gcd(e1,e2)=g>1` → the identity gives `m^g`; rescue
only if `m^g < n` (`nth-root`), else dead.

## The verify

`pow(m,e1,n)==c1` **and** `pow(m,e2,n)==c2` — both must hold.

## The traps

- The **same `m`** is required — a pad or a different `m` yields `m1^a·m2^b`.
- `gcd>1` → `m^g`; the check `pow(m^g, 1, n)` won't reproduce `c`.
- The negative Bezout coefficient needs `pow(c,-k,n)` — the modular inverse,
  not a literal `c**-k`.
