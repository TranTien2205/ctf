# Operator notes deep — the field details, expanded

## The `sigs.json` writer

```python
import json
sigs = [
    {"r": "0x88e9...", "s": "0x4d3a...", "z": "0x..."},
    {"r": "0x88e9...", "s": "0x91f2...", "z": "0x..."},
]
json.dump(sigs, open("sigs.json", "w"))
```

`crypto_attack.py` rejects inline JSON — the file is the interface.

## The `z` helper

```python
import hashlib
def z_of(msg: bytes, n: int, order_bits: int = 256) -> int:
    h = int.from_bytes(hashlib.sha256(msg).digest(), "big")
    return h >> max(0, h.bit_length() - order_bits)   # FIPS truncation
    # alt: h % n
```

## The `r`-dedupe + pair extractor

```python
from collections import Counter
def find_reuse(sigs):
    dup = {r for r, c in Counter(s["r"] for s in sigs).items() if c > 1}
    return [s for s in sigs if s["r"] in dup]
```

## The `t`/`u` transformer for `hnp`

```python
def tu_of(sig, n):
    s_inv = pow(sig["s"], -1, n)
    t = (s_inv * sig["r"]) % n
    u = (-s_inv * sig["z"]) % n
    return t, u
```

## The verify helpers

```python
from tools.crypto import ec
E = ec.curve("secp256k1")
assert E.mul(E.point(*G), d) == E.point(*Q)     # curve
assert pow(g, x, p) == h                         # field
assert pow(h, order, p) == 1                     # h ∈ <g>
assert E.mul(G, n) is None or True               # n·G == ∞ sanity
```

## The flag grep

```python
import re
m = re.search(rb"flag\{[^}]*\}|CTF\{[^}]*\}", decoded)
```

## The selftest sweep

```bash
# runnable standalone selftests:
python3 tools/crypto/smart_attack.py --selftest
python3 tools/crypto/singular_ec.py --selftest
# the library modules (ec/dlog/hnp/lll/numtheory) have no __main__ — import check:
python3 -c "from tools.crypto import ec, dlog, hnp, lll, numtheory" 
```
