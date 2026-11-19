# Operator notes — the field details

## The `--sigs` workflow

```bash
cat > sigs.json <<'EOF'
[{"r": 110538, "s": 2994796, "z": 12007884},
 {"r": 110538, "s": 4239087, "z": 9080421}]
EOF
python3 tools/crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order <n>
```

## The `z` helper

```python
import hashlib
def z_of(msg: bytes, order_bits: int = 256) -> int:
    h = int.from_bytes(hashlib.sha256(msg).digest(), 'big')
    return h >> max(0, h.bit_length() - order_bits)  # FIPS truncation
    # alt: return h % n
```

## The `r`-dedupe helper

```python
from collections import Counter
dup = [r for r, c in Counter(s["r"] for s in sigs).items() if c > 1]
pairs = [s for s in sigs if s["r"] in dup]
```

## The verify helper

```python
from tools.crypto import ec
E = ec.curve({"p": p, "a": a, "b": b})
assert E.mul(E.point(*G), d) == E.point(*Q)   # d·G == Q
```

## The `selftest` gate

```bash
python3 -c "from tools.crypto import hnp"   # library module — no __main__
python3 -c "from tools.crypto import dlog"   # library module — no __main__
python3 -c "from tools.crypto import lll"   # library module — no __main__
python3 tools/crypto/smart_attack.py --selftest
python3 tools/crypto/singular_ec.py --selftest
```

## The flag grep

```python
re.search(rb'flag\{[^}]*\}|CTF\{[^}]*\}', decoded)
```
