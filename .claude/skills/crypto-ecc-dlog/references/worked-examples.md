# Worked examples — end-to-end solves

## Example 1 — `ecdsa-nonce-reuse` on two signatures

Handout: two signatures on `secp256k1`, `r` identical:

```
sigs.json:
[{"r": 110538, "s": 2994796, "z": 12007884},
 {"r": 110538, "s": 4239087, "z": 9080421}]
```

```bash
python3 tools/crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json \
  --order 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
```

→ `d`. Verify `d·G == Q`, decrypt, flag.

## Example 2 — `hnp-ecdsa` on a signing oracle

Service signs with a 128-bit nonce on P-256. Collect ~4 sigs (`z` =
`sha256(m)` truncated), all `r` distinct:

```bash
python3 tools/crypto_attack.py hnp-ecdsa --sigs sigs.json \
  --order 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551 \
  --nonce-bits 128 --curve secp256r1 --pubkey 04...
```

→ `d`. Verify `d·G == Q`.

## Example 3 — `pohlig-hellman` on a smooth order

`h = g^x mod p`, `p = 7861`, `ord(g) = p-1 = 7860 = 2²·3·5·131`:

```bash
python3 tools/crypto_attack.py smoothness --n 7860   # largest factor 131 — fine
python3 tools/crypto_attack.py pohlig-hellman --g 2 --h 6174 --p 7861 --order 7860
```

→ `x`. Verify `pow(g, x, p) == h`.

## Example 4 — `bsgs` on a bounded secret

`h = g^x mod p`, `x` stated `< 2^20`:

```bash
python3 tools/crypto_attack.py bsgs --g 5 --h 17 --p 104729 --order 2**20
```

(Or `dlog.bsgs(g, h, p, order=1<<20)` in code.)

## Example 5 — smart_attack on a custom curve

Handout gives `p, a, b`; counting shows `#E == p`:

```python
from tools.crypto import smart_attack
x = smart_attack.solve(P, Q, a, b, p)   # module CLI: --selftest
```

## Example 6 — singular cubic

`Δ ≡ 0` → `singular_ec.py` maps to `Fp*`, then `pohlig-hellman` on `p-1`.
