# Detection — reading the handout before any math

## What arrives

A handout for this class carries one of:

- **ECDSA signature pairs** `(r, s)` plus a message / hash `z` and a public
  key `Q` — nonce attacks live here.
- **A discrete-log statement** `h = g^x mod p` or `Q = x·G` on a named or
  custom curve — DLP attacks live here.
- **Curve parameters** `(p, a, b, G, n)` — possibly a vulnerable custom curve.
- **A signing service** — `sign(message) -> (r, s)` endpoint or binary —
  oracle-driven nonce recovery.

## Step 0 — name the group

Before any statistic: curve name, field size, order `n`, generator. The
discriminator reads differently per group:

| Group | Reads |
|---|---|
| `secp256k1`, `NIST P-256/384`, `Curve25519` | real curves — attacks are nonce or implementation bugs |
| custom `p, a, b` | check `n == p` (anomalous → smart_attack), singular curve (singular_ec), smooth `n` (pohlig-hellman) |
| `y = g^x mod p` | multiplicative group — check `p-1` smoothness first |
| pairing-friendly curve | MOV/Frey-Rück transfer possible (small embedding degree) |

## Step 1 — the discriminator

| Observation | Attack | Command |
|---|---|---|
| two signatures share `r` | `ecdsa-nonce-reuse` — closed form | `crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order n` |
| many signatures, distinct `r`, short/biased/partial `k` | `hnp-ecdsa` — lattice | `crypto_attack.py hnp-ecdsa --sigs sigs.json --order n --nonce-bits B` |
| nonce leaks MSB/LSB bits directly | `hnp` / `hnp-ecdsa` | `crypto_attack.py hnp-ecdsa --sigs … --nonce-bound B` |
| `p-1` or `ord(g)` smooth | `pohlig-hellman` | `crypto_attack.py pohlig-hellman --g g --h h --p p --order n` |
| small group / bounded `x < B` | `bsgs` | `crypto_attack.py bsgs --g g --h h --p p --order n` |
| `n == p` on custom curve | Smart's anomalous attack | `tools/crypto/smart_attack.py` |
| `disc(a,b) = 4a³+27b² ≡ 0` | singular cubic → linear dlog | `tools/crypto/singular_ec.py` |
| order unknown | `smoothness --n n` then order tooling | `crypto_attack.py smoothness --n n` |

## Step 2 — always run the cheap checks first

1. `crypto_attack.py smoothness --n <order>` — seconds, decides PH vs BSGS.
2. Scan all `r` values for a duplicate — `ecdsa-nonce-reuse` needs no lattice.
3. Check `n == p` on custom curves — Smart's attack is linear time.
4. Check the discriminant — singular curves are trivially broken.

## What detection is NOT

No detection step *proves* the attack works — the falsifier per attack
module does that. Detection picks the cheapest compatible attack first.
