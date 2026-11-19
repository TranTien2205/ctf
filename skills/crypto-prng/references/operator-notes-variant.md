# Operator notes variant — the helper snippets

## Collect + normalize

```python
outs = []
for line in open("responses.txt"):
    v = line.strip()
    v = int(v, 16) if v.startswith("0x") else int(v)   # decode
    outs.append(v)
```

## The gcd fingerprint

```python
from math import gcd
from functools import reduce
ts = [outs[i+1]-outs[i] for i in range(len(outs)-1)]
m = reduce(gcd,(ts[i+1]*ts[i-1]-ts[i]*ts[i] for i in range(1,len(ts)-1)),0)
```

## The seed loop

```python
import random
for ts in range(iat-5, iat+5):
    r = random.Random(ts)
    if r.getrandbits(32) == o0 and r.getrandbits(32) == o1:
        seed = ts; break
```

## The LCG verify

```python
assert (a*outs[-1]+c) % m == held_back
```

## The bit list for LFSR

```python
print(",".join(str(b) for b in bits))       # --bits wants commas
open("bits.txt","w").write("".join(map(str,bits)))  # --bits-file
```

## The flag grep

```python
import re
re.search(rb"flag\{[^}]*\}|CTF\{[^}]*\}", recovered)
```

## The selftest

```bash
python3 tools/crypto/xorshift128.py --selftest
python3 tools/crypto_attack.py list
```
