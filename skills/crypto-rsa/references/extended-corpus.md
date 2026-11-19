# Extended corpus — the additional reads, shapes, and chains

## The `.der` ASN.1 read

```bash
openssl asn1parse -inform DER -in key.der
# SEQUENCE { INTEGER n, INTEGER e, [INTEGER d, INTEGER p, INTEGER q, ...] }
```

A private `.der` carries `d`,`p`,`q`,`dp`,`dq`,`qInv` — `factor-from-d`/`crt`.

## The `openssl`/`Crypto` reads

```python
from Crypto.PublicKey import RSA
k = RSA.importKey(open('key.pem').read())
k.n, k.e                    # public
k.d, k.p, k.q, k.u          # if private — u = qInv
```

## The `signature` reads

```python
# a PKCS1 v1.5 signature — the padded m
s = int(sig); m = pow(s, e, n)     # the padded block — unpad for the flag
```

## The CRT exponents

```python
# dp, dq, qInv held → p,q
for k in range(1, e):
    p = (e*dp - 1)//k + 1
    if n % p == 0: break
```

## The `n` shape checks

```python
from sympy import isqrt, factorint, isprime
if isqrt(n)**2 == n:        # n = p²
if isprime(n):              # n prime → phi = n-1
fac = factorint(n)          # n smooth → the factors
```

## The wrap check

```python
m_bits = 8*len(flag)                       # or a guessed m length
wraps = m_bits*e < n.bit_length()          # m^e < n → small-e
```

## The `e`-attack checks

```python
e_bits = e.bit_length(); n_bits = n.bit_length()
if e_bits >= n_bits - 2:    # e ≈ n → small d → wiener/boneh-durfee
```

## The `hastad` check

```python
# len(ns) >= e, all pairwise coprime, no pad
gcds = [gcd(ns[i],ns[j]) for i in range(len(ns)) for j in range(i+1,len(ns))]
assert all(g==1 for g in gcds)
```

## The verify

`pow(m,e,n)==c` / `p*q==n`.
