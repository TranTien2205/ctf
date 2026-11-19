# Operator notes — the field details

## The `outputs` writer

```python
import json
outs = [14234, 99215, 31157]      # raw ints
open("outs.txt","w").write(",".join(map(str,outs)))
```

`--outputs` is comma-separated; `--outputs-file`/`--in` for files/JSON.

## The normalizer

```python
outs = [int(x,16) if isinstance(x,str) and x.startswith('0x') else
        int(x) if isinstance(x,str) else x for x in outs]
# floats -> int(v * 2**53) for random.random pairs
```

## The fingerprint helpers

```python
from math import gcd
# LCG modulus guess:
ts = [x[i+1]-x[i] for i in range(len(x)-1)]
m = 0
for i in range(1,len(ts)-1):
    m = gcd(m, ts[i+1]*ts[i-1] - ts[i]*ts[i])
```

## The selftest sweep

```bash
python3 tools/crypto/xorshift128.py --selftest        # standalone
python3 tools/crypto_attack.py list                 # inventory
python3 -c "from tools.crypto import lcg,lfsr,mt19937"  # library check
```

## The `predict` verifier

```python
assert predict_next == held_back    # never skip
```

## The flag grep

```python
import re
m = re.search(rb"flag\{[^}]*\}|CTF\{[^}]*\}", decoded)
```
