# Recon order deep — the full first-pass, annotated

## 0 — the artifact inventory

```bash
ls -la; file *; xxd <bin> | head -20
python3 tools/crypto_attack.py list    # every attack id + its bound + lll_backend
```

The files and the inventory. Note every key/cert/json/txt/py/bin/pcap.

## 1 — the key reads

```python
from Crypto.PublicKey import RSA
import glob, json
for f in glob.glob('*'):
    try:
        if f.endswith(('.pem','.der','.key','.crt','.pub')):
            k = RSA.importKey(open(f,'rb').read())
            print(f, k.n.bit_length(), 'e=%d'%k.e, 'priv=%s'%k.has_private())
            if k.has_private(): print('  d=%d p=%d q=%d'%(k.d,k.p,k.q))
    except Exception as ex: pass
```

`n` bits, `e`, and any private fields (`d`,`p`,`q` → `factor-from-d`/`crt`).

## 2 — the integer read

```python
import re
for f in ['out.txt','output.txt','chal_out.txt','messages.txt','keys.json']:
    try:
        s = open(f).read()
        ints = re.findall(r'(?:0x)?[0-9a-fA-F]{20,}|\b\d{20,}\b', s)
        print(f, len(ints), 'ints:', [len(i) for i in ints[:10]])
    except: pass
```

Count the `n`,`e`,`c` integers — `n`≥2 → `batch-gcd`/`hastad`; `e`×2 →
`common-modulus`; `c`≥`e` → `hastad`.

## 3 — the keygen read

```bash
grep -nE "getPrime|next_prime|seed|random|e ?=|e=|inverse|p-1|p\+1|m2|dp|dq|qInv|print|redact|XXXX|mask|pad|os.urandom|sha|flag" chal.py keygen.py gen.py 2>/dev/null
```

The misuse line — the tell.

## 4 — the cheap discriminating reads

```python
from math import gcd
from sympy import isqrt, factorint, isprime, integer_nthroot
# the counts
print('n:', n.bit_length(), 'e:', e, 'e_bits:', e.bit_length())
# the degenerate
print('n square:', isqrt(n)**2==n, 'prime:', isprime(n))
fac = factorint(n, limit=10**6); print('small factors:', fac)
# the wrap
print('m^e<n (if m guess):', m**e < n)
# the gcd
print('gcd(e,phi):', gcd(e,phi) if 'phi' in dir() else '?')
```

## 5 — the sheet + the route

Fill `parameter-sheet.md` → `attack-table.md` → `per-bound.md` → the attack.
