# Operator notes deep — the helpers, fully written

## The outputs writer — every form

```python
import json
outs = [15323, 22011, 4421, 9917]           # raw ints

# --outputs form: comma-separated
print(",".join(map(str, outs)))

# --outputs-file form: one per line or a JSON list
open("outs.txt","w").write("\n".join(map(str,outs)))
open("outs.json","w").write(json.dumps({"outputs": outs}))

# --bits form for LFSR: comma 0/1
print(",".join(str(b) for b in bits))
```

## The normalizer — every shape

```python
def norm(v):
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("0x"):  return int(v, 16)
        if v.startswith("0b"):  return int(v, 2)
        try: return int(v)
        except ValueError:      # a float
            return int(float(v) * 2**53)
    return v
outs = [norm(x) for x in raw]
```

## The fingerprint — every test

```python
from math import gcd
# LCG modulus guess — telescope gcd
def guess_m(x):
    ts = [x[i+1]-x[i] for i in range(len(x)-1)]
    m = 0
    for i in range(1, len(ts)-1):
        m = gcd(m, ts[i+1]*ts[i-1] - ts[i]*ts[i])
    return abs(m)

# LFSR linear-complexity hint (cheap)
# run berlekamp-massey — its L output IS the fingerprint

# MT test — just try the clone; predict==held is the proof
```

## The seed enumerator — every platform

```python
import random
# Python random (MT19937)
for ts in range(lo, hi):
    if random.Random(ts).getrandbits(32) == o0: seed = ts

# java.util.Random (48-bit LCG)
def jrand(seed):
    s = (seed ^ 0x5DEECE66D) & (2**48 - 1)
    s = (s * 0x5DEECE66D + 0xB) & (2**48 - 1)
    return s >> 16              # nextInt

# glibc rand (additive — needs history, not a plain LCG)
```

## The `predict` verifier — every attack

```python
# LCG
assert (a*o_last + c) % m == held
# LFSR
assert lfsr_predict(bits, taps, w, k) == held_bits[:k]
# MT
assert clone.getrandbits(32) == o624
# xorshift
assert predict == o4
# seed
r = random.Random(seed); assert r.getrandbits(32)==o0 and r.getrandbits(32)==o1
```

## The selftest sweep — the real commands

```bash
python3 tools/crypto/xorshift128.py --selftest   # standalone CLI
python3 tools/crypto_attack.py list              # the attack inventory
python3 -c "from tools.crypto import lcg, lfsr, mt19937, xorshift128"  # lib
```

`lcg/lfsr/mt19937` are LIBRARY modules — import them; only `xorshift128`
is a runnable CLI among them.

## The flag grep

```python
import re
m = re.search(rb"flag\{[^}]*\}|CTF\{[^}]*\}", recovered_bytes)
```
