# Worked examples — the full solve, from sheet to flag

## Example 1 — fermat (close primes)

**Sheet**: `n = p·q`, `e=65537`, `c`. Keygen: `q = next_prime(p)`.
**Discriminator**: `p`,`q` close → `fermat`.
```python
from sympy import integer_nthroot, isqrt
a = isqrt(n) + 1
while True:
    b, ok = integer_nthroot(a*a - n, 2)
    if ok: p, q = a+b, a-b; break
    a += 1
phi=(p-1)*(q-1); d=pow(65537,-1,phi); m=pow(c,d,n)
assert p*q==n and pow(m,65537,n)==c
```
**Or**: `crypto_attack.py fermat --n <n>` → `rsa-decrypt`.

## Example 2 — wiener (small d)

**Sheet**: `n`,`e`,`c`; `e` ~ `n` bits.
**Discriminator**: `e` large → `d` small → `wiener`.
```bash
crypto_attack.py wiener --n <n> --e <e>   # convergents of e/n → d
crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
```
**Verify**: `pow(c,d,n)==m`, `pow(m,e,n)==c`.

## Example 3 — batch-gcd

**Sheet**: `keys.json` — 30 `n`,`e`,`c` triples.
**Discriminator**: `n` count ≥ 2 → `batch-gcd`.
```python
from math import gcd
ns=[...]
for i in range(len(ns)):
  for j in range(i+1,len(ns)):
    g=gcd(ns[i],ns[j])
    if g>1: print(i,j,'shared',g)
```
**Verify**: `p*q==n` → `rsa-decrypt` → `pow==c`.

## Example 4 — hastad

**Sheet**: `e=3`, `c1,c2,c3` under `n1,n2,n3`, same `m`.
**Discriminator**: `c` count ≥ `e` → `hastad`.
```python
from sympy.ntheory.modular import crt
from sympy import integer_nthroot
x = crt([n1,n2,n3],[c1,c2,c3])[0]
m,ok = integer_nthroot(x,3); assert pow(m,3)==x
```
**Verify**: `pow(m,3)==x` → the flag.

## Example 5 — common-modulus

**Sheet**: `n`,`e1`=3,`e2`=17,`c1`,`c2` same `m`.
```python
g,a,b = ...ext_gcd(3,17)...   # a*3 + b*17 = 1
m = pow(c1,a,n) * pow(c2,b,n) % n
assert pow(m,3,n)==c1
```

## Example 6 — pollard-pm1

**Sheet**: `n`,`e`,`c`; keygen "p chosen weak".
```python
import math
a=2; B=100000
for j in range(2,B+1): a=pow(a,j,n)
g=math.gcd(a-1,n)   # >1 → p
```

## Example 7 — coppersmith partial p

**Sheet**: `p`'s top bits known (`a`), `unknown-bits`=256.
```bash
crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits 256
# → x → p=a+x → factor-from-d → rsa-decrypt
```

## Example 8 — eth-root

**Sheet**: `n`,`e`,`c`; `gcd(e,phi)=3`; `p`,`q` held.
```bash
crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"
# the gcd candidates; pow(m,e,n)==c + flag format picks
```
