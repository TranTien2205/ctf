# Payload dictionary — every command this class uses

## `crypto_attack.py` attack commands

```bash
# the smoothness check — always first for dlog
python3 tools/crypto_attack.py smoothness --n 1092924092708206891

# ECDSA — two signatures, same r
python3 tools/crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# ECDSA — biased/short/partial nonce (lattice)
python3 tools/crypto_attack.py hnp-ecdsa --sigs sigs.json --order 0xFF...FF --nonce-bits 128
python3 tools/crypto_attack.py hnp-ecdsa --sigs sigs.json --order 0xFF...FF --nonce-bound 0x100000000000000000000000000000000
python3 tools/crypto_attack.py hnp-ecdsa --sigs sigs.json --order 0xFF...FF --nonce-bits 128 --curve secp256k1 --pubkey "04..."

# raw HNP
python3 tools/crypto_attack.py hnp --t t.json --u u.json --modulus n --bound B

# DLP — smooth order
python3 tools/crypto_attack.py pohlig-hellman --g 2 --h 17 --p 101 --order 100

# DLP — bounded exponent / small group
python3 tools/crypto_attack.py bsgs --g 2 --h 17 --p 101 --order 100
```

## `crypto_attack.py` utility commands

```bash
python3 tools/crypto_attack.py list          # every attack + applicability
python3 tools/crypto_attack.py list --json   # machine-readable
python3 tools/crypto_attack.py describe hnp-ecdsa   # flags + applicability
```

## Standalone `tools/crypto/` modules

```bash
python3 tools/crypto/smart_attack.py --selftest    # anomalous-curve solver
python3 tools/crypto/singular_ec.py --selftest     # singular-cubic solver
python3 -c "from tools.crypto import dlog"   # library module — no __main__            # PH + BSGS
python3 -c "from tools.crypto import hnp"   # library module — no __main__             # HNP lattice
python3 -c "from tools.crypto import lll"   # library module — no __main__             # pure-python LLL
```

In code:

```python
from tools.crypto import ec, smart_attack, singular_ec, dlog, hnp

E = ec.curve("secp256k1")            # or ec.curve({"p":..., "a":..., "b":...})
x = dlog.pohlig_hellman(g, h, p, order)
x = dlog.bsgs(g, h, p, order)
d = hnp.ecdsa_recover_nonce_reuse(sig_a, sig_b, order)
d = hnp.ecdsa_recover_biased_nonce(sigs, order, nonce_bits=128)
need = hnp.required_signatures(order_bits=256, nonce_bits=8)
```

## The `--sigs` JSON file

```json
[{"r": 10, "s": 20, "z": 30}, {"r": 10, "s": 40, "z": 50}]
```
