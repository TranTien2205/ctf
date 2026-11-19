# Detection playbook — the commands that fill the sheet

## The inventory

```bash
python3 tools/crypto_attack.py list     # the ids + bounds + lll_backend
```

## The keys

```python
from Crypto.PublicKey import RSA
k = RSA.importKey(open('key.pem').read())
print(k.n.bit_length(), k.e, k.has_private())
```

## The integers

```python
import re
s = open('out.txt').read()
ints = re.findall(r'(?:0x)?[0-9a-fA-F]{20,}|\b\d{20,}\b', s)
```

## The keygen

```bash
grep -nE "getPrime|next_prime|seed|e ?=|inverse|p-1|m2|dp|dq|qInv|print|redact|pad" chal.py
```

## The cheap reads

```python
from math import gcd
from sympy import isqrt, factorint, isprime
print('n bits:', n.bit_length(), 'e:', e, 'e bits:', e.bit_length())
print('square:', isqrt(n)**2==n, 'prime:', isprime(n))
print('small factors:', factorint(n, limit=10**6))
print('m^e<n:', m**e < n if m else '?')
if 'phi' in dir(): print('gcd(e,phi):', gcd(e,phi))
```

## The route

`attack-table.md` → `per-bound.md` → `crypto_attack.py <id>` → `verify.md`.
