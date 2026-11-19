# Worked examples deep — annotated solves

## `ecdsa-nonce-reuse` — full transcript

Two P-256 signatures:

```
sig1: r=0x88e9.., s=0x4d3a.., z=sha256("msg1")
sig2: r=0x88e9.., s=0x91f2.., z=sha256("msg2")
```

```bash
cat > sigs.json <<'EOF'
[{"r":"0x88e9..","s":"0x4d3a..","z":"0x.."},
 {"r":"0x88e9..","s":"0x91f2..","z":"0x.."}]
EOF
python3 tools/crypto_attack.py ecdsa-nonce-reuse \
  --sigs sigs.json --order 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
```

Output `d`. Then:

```python
from tools.crypto import ec
E = ec.curve("secp256r1")
assert E.mul(E.point(*G), d) == E.point(*Q)
```

## `hnp-ecdsa` — full transcript

Oracle `sign(m)` on secp256k1, nonce "128 bits". Collect 6 sigs:

```bash
cat > sigs.json <<'EOF'
[{"r": .., "s": .., "z": ..}, ...]
EOF
python3 tools/crypto_attack.py hnp-ecdsa \
  --sigs sigs.json \
  --order 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 \
  --nonce-bits 128 --curve secp256k1 --pubkey "04..."
```

## `pohlig-hellman` — full transcript

`h = g^x mod p`, `p = 7861`, `ord(g) = 7860 = 2²·3·5·131`:

```bash
python3 tools/crypto_attack.py smoothness --n 7860
python3 tools/crypto_attack.py pohlig-hellman --g 2 --h 6174 --p 7861 --order 7860
```

`x` → verify `pow(2, x, 7861) == 6174`.

## `bsgs` — full transcript

`h = g^x mod p`, `x < 2^20`:

```bash
python3 tools/crypto_attack.py bsgs --g 5 --h 17 --p 104729 --order 1048576
```

## `smart_attack` — full transcript

Custom `p, a, b`, `#E == p`:

```python
from tools.crypto import smart_attack
x = smart_attack.solve(P, Q, a, b, p)   # module; --selftest confirms
```

## `singular_ec` — full transcript

`Δ ≡ 0 mod p` → `singular_ec.py` maps to `Fp*`, `pohlig-hellman` on `p-1`.
