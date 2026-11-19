# Theory playbook — the maths you actually run

## The RSA identity

```python
# n = p*q; phi = (p-1)*(q-1); ed ≡ 1 mod phi
# c = m^e mod n;  m = c^d mod n
# verify: pow(m, e, n) == c
```

## The exact root

```python
from sympy import integer_nthroot
m, exact = integer_nthroot(c, e)
assert exact and pow(m, e) == c      # no mod n — the wrap never happened
```

## CRT + root (Håstad)

```python
from sympy.ntheory.modular import crt
x = crt([n1,n2,n3], [c1,c2,c3])[0]   # x = m^e mod ∏ni
m, _ = integer_nthroot(x, e)
assert pow(m, e) == x
```

## Fermat

```python
a = isqrt(n) + 1
while True:
    b, ok = integer_nthroot(a*a - n, 2)
    if ok: p, q = a+b, a-b; break
    a += 1
```

## The gcd splits

```python
from math import gcd
gcd(ni, nj)            # batch-gcd → shared p
gcd(pow(a, B_factorial, n) - 1, n)   # pollard-pm1 → p
gcd(pow(a, e*dp - 1, n) - 1, n)      # leaked dp → p
gcd(pow(s_faulty, e, n) - m, n)      # Bellcore → q
```

## Bezout (common-modulus)

```python
g, a, b = ext_gcd(e1, e2)            # a*e1 + b*e2 = 1
m = (pow(c1, a, n) * pow(c2, b, n)) % n
```

## Wiener CF

```python
# convergents ki/di of e/n → phi'=(e*di-1)/ki → x²-(p+q)x+n=0
```

## Boneh-Durfee

```python
# f(x,y)=x(A-y)+1 mod e, A=n+1; lattice for (k, p+q); d<n^0.292
```

## Coppersmith

```python
# f(x)=a+x ≡ 0 mod p, x<n^0.25 → LLL → x → p
```

## The verify

```python
assert pow(m, e, n) == c
assert p * q == n
```
