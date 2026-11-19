# Payload dictionary variant — the commands, compact

## The nonce commands

```bash
# r dedupe → reuse
python3 tools/crypto_attack.py ecdsa-nonce-reuse --sigs f.json --order n
# k bounded → lattice
python3 tools/crypto_attack.py hnp-ecdsa --sigs f.json --order n --nonce-bits B
python3 tools/crypto_attack.py hnp-ecdsa --sigs f.json --order n --nonce-bound B
# (t,u) leak → lattice
python3 tools/crypto_attack.py hnp --t t.json --u u.json --modulus n --bound B
```

## The dlog commands

```bash
python3 tools/crypto_attack.py smoothness --n ord
python3 tools/crypto_attack.py pohlig-hellman --g g --h h --p p --order ord
python3 tools/crypto_attack.py bsgs --g g --h h --p p --order B
```

## The defect commands

```bash
python3 tools/crypto/smart_attack.py --p P --a A --b B --gx GX --gy GY --qx QX --qy QY --order P
python3 tools/crypto/singular_ec.py --p P --a2 0 --a1 A --a0 B --gx GX --gy GY --qx QX --qy QY
python3 -c "from tools.crypto import ec"   # library module — no __main__
```

## The helper invocations

```python
from tools.crypto import ec, dlog, hnp, lll, numtheory
E = ec.curve("secp256k1")            # or ec.Curve(p,a,b)
E.mul(G_pt, k)                       # curve scalar mul
dlog.pohlig_hellman(g, h, p, ord)    # direct call
dlog.bsgs(g, h, p, B)                # direct call
numtheory.smoothness(n, B)           # factor test
```

## The selftests

```bash
# runnable standalone selftests:
python3 tools/crypto/smart_attack.py --selftest
python3 tools/crypto/singular_ec.py --selftest
# the library modules (ec/dlog/hnp/lll/numtheory) have no __main__ — import check:
python3 -c "from tools.crypto import ec, dlog, hnp, lll, numtheory" 
python3 tools/crypto_attack.py list
```
