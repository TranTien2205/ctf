# Detection playbook deep — the commands that fill the sheet

## The artifact inventory

```bash
ls; file *; xxd <bin> | head     # the types
python3 tools/crypto_attack.py list   # the inventory + bounds
```

## The key fields

```python
from Crypto.PublicKey import RSA
import glob, json
for f in glob.glob('*'):
    try:
        if f.endswith(('.pem','.der','.key','.crt')):
            k = RSA.importKey(open(f,'rb').read())
            print(f, k.n.bit_length(), 'e=%d'%k.e, 'priv=%s'%k.has_private())
        elif f.endswith('.json'):
            d = json.load(open(f)); print(f, list(d)[:6])
    except Exception as ex: print(f, type(ex).__name__)
```

## The integers

```python
import re
s = open('out.txt').read()
ints = re.findall(r'(?:0x)?[0-9a-fA-F]{20,}|\b\d{20,}\b', s)
print(len(ints), 'integers')
```

## The cheap discriminating reads

```python
from math import gcd
from sympy import isqrt, factorint, isprime
# the counts, the degenerate, the wrap, the small-e, the gcd
print('n square:', isqrt(n)**2 == n)
print('n prime:', isprime(n))
print('gcd(e,phi):', gcd(e, phi) if phi else 'phi?')
print('m^e<n:', m**e < n)
```

## The keygen read

```bash
grep -nE "getPrime|next_prime|seed|e ?=|inverse|p-1|m2|dp|dq|qInv|print|redact|pad|os.urandom" chal.py keygen.py
```

## The route

`attack-table.md` — the first-yes row. `per-bound.md` — the falsifier.
