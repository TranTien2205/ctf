# Payload dictionary deep — every command with every flag

## `crypto_attack.py` — full flags

```bash
# the gate — factor an order
python3 tools/crypto_attack.py smoothness --n 1092924092708206891

# ECDSA — two signatures, same r
python3 tools/crypto_attack.py ecdsa-nonce-reuse \
  --sigs sigs.json \
  --order 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# ECDSA — biased/short nonce
python3 tools/crypto_attack.py hnp-ecdsa \
  --sigs sigs.json \
  --order 0xFF...FF \
  --nonce-bits 128
# or --nonce-bound 0x100000000000000000000000000000000
# optional self-verify: --curve secp256k1 --pubkey 04...

# raw HNP — (t, u) pairs
python3 tools/crypto_attack.py hnp \
  --t t.json --u u.json --modulus 0xFF...FF --bound 0x1000...

# DLP — smooth order
python3 tools/crypto_attack.py pohlig-hellman \
  --g 2 --h 17 --p 101 --order 100

# DLP — bounded / small
python3 tools/crypto_attack.py bsgs \
  --g 2 --h 17 --p 101 --order 100

# utility
python3 tools/crypto_attack.py list
python3 tools/crypto_attack.py list --json
python3 tools/crypto_attack.py describe hnp-ecdsa
```

## The `--sigs` file format, complete

```json
[
  {"r": "0xabc...", "s": "0xdef...", "z": "0x123..."},
  {"r": 12345, "s": 67890, "z": 111213},
  [1, 2, 3]
]
```

- `r`, `s` — signature ints (hex `"0x..."` or decimal).
- `z` — the message hash *as integer*; hash the message first if the handout
  gives raw text (`sha256(m)` truncated to `order_bits`, else `mod n`).

## The standalone modules

```bash
python3 tools/crypto/smart_attack.py --selftest
python3 tools/crypto/singular_ec.py --selftest
python3 -c "from tools.crypto import dlog"   # library module — no __main__
python3 -c "from tools.crypto import hnp"   # library module — no __main__
python3 -c "from tools.crypto import lll"   # library module — no __main__
python3 -c "from tools.crypto import ec"   # library module — no __main__
```

In code:

```python
from tools.crypto import ec, smart_attack, singular_ec, dlog, hnp, numtheory
E = ec.curve("secp256k1")  # or ec.curve({"p": p, "a": a, "b": b})
x = dlog.pohlig_hellman(g, h, p, order)
x = dlog.bsgs(g, h, p, order)
f = numtheory.smoothness(n)
d = hnp.ecdsa_recover_nonce_reuse(sig_a, sig_b, order)
d = hnp.ecdsa_recover_biased_nonce(sigs, order, nonce_bits=128, curve=..., pubkey=...)
need = hnp.required_signatures(order_bits=256, nonce_bits=128)
```
