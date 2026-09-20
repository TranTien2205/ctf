# RSA Attack Techniques

## Factorization Attacks

### Small Modulus
```bash
# factordb.com
# yafu
yafu "factor(N)"
# msieve
msieve -v N
```

### Wiener Attack (Small Private Exponent)
```bash
# Use RsaCtfTool
python3 RsaCtfTool.py --publickey pub.pem --private

# Or use wiener-attack implementation
```

### Fermat Factorization
```python
import gmpy2

def fermat_factor(n):
    a = gmpy2.isqrt(n) + 1
    b2 = a*a - n
    while not gmpy2.is_square(b2):
        a += 1
        b2 = a*a - n
    b = gmpy2.isqrt(b2)
    return int(a-b), int(a+b)
```

### Known Factorization
```python
# factordb.com for pre-computed factorizations
# Common primes in CTF
```

## Common Modulus Attack
```python
# Same n, different e (e1, e2 coprime)
# c1 = m^e1 mod n
# c2 = m^e2 mod n
import gmpy2
g, u, v = gmpy2.gcdext(e1, e2)
m = (pow(c1, u, n) * pow(c2, v, n)) % n
```

## Hastad Broadcast Attack
```python
# Same m, different n, e=3
# Chinese Remainder Theorem
from functools import reduce
import gmpy2

def crt(moduli, remainders):
    M = reduce(lambda x, y: x*y, moduli)
    x = 0
    for i in range(len(moduli)):
        Mi = M // moduli[i]
        yi = int(gmpy2.invert(Mi, moduli[i]))
        x += remainders[i] * Mi * yi
    return x % M

# m = CRT(ciphertexts, moduli)
# m_cubed = m
# m = iroot(m_cubed, 3)
```

## Bleichenbacher Attack (e=3)
```python
import gmpy2
# If m^3 < n
m = gmpy2.iroot(c, 3)[0]
```

## Coppersmith Attack
```python
# Small message with known padding
# Use SageMath
# Wiener with Coppersmith
```

## Low Public Exponent
```python
# e=3, small m
m = gmpy2.iroot(c, 3)[0]

# e=3 with padding
# Try adding multiples of n until cube root is integer
for k in range(1000):
    m, exact = gmpy2.iroot(c + k*n, 3)
    if exact:
        print(f"k={k}, m={m}")
```

## RSA Key Reading Template
```python
from Crypto.PublicKey import RSA
import gmpy2

key = RSA.import_key(open('pub.pem').read())
n = key.n
e = key.e

# If you have d
phi = (p-1)*(q-1)
d = gmpy2.invert(e, phi)
m = pow(c, d, n)

# If factoring
# Use yafu, msieve, or online tools
# factordb.com for large numbers
```

## PRNG Prediction (if RSA uses weak RNG for key generation)
```python
import random
import time
# If seed is time-based
for seed in range(int(time.time())-100, int(time.time())+100):
    random.seed(seed)
    if random.getrandbits(32) == target:
        print(f'Seed: {seed}')
```

## Tools
```
RsaCtfTool       # Automated RSA attacks
factordb.com     # Factor database
yafu             # Integer factorization
SageMath         # Complex math
```
