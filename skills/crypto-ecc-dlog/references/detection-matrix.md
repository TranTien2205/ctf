# Detection matrix — observation → attack → command

| Observation | Check | Attack | Command |
|---|---|---|---|
| two `r` equal | — | `ecdsa-nonce-reuse` | `crypto_attack.py ecdsa-nonce-reuse --sigs f --order n` |
| `k` bounded, sigs ≥ count | `required_signatures` | `hnp-ecdsa` | `crypto_attack.py hnp-ecdsa --sigs f --order n --nonce-bits B` |
| `(t,u)` pairs | — | `hnp` | `crypto_attack.py hnp --t f --u f --modulus n --bound B` |
| `ord(g)`/`#E` smooth | `smoothness --n` | `pohlig-hellman` | `crypto_attack.py pohlig-hellman --g g --h h --p p --order n` |
| `x`/order bounded | — | `bsgs` | `crypto_attack.py bsgs --g g --h h --p p --order n` |
| `#E == p` | `#E` | `smart_attack` | `tools/crypto/smart_attack.py` |
| `Δ == 0` | `4a³+27b² mod p` | `singular_ec` | `tools/crypto/singular_ec.py` |
| server skips on-curve check | submit point | invalid curve | `tools/crypto/ec.py` + `bsgs`/`pohlig` |
| unknown order | — | `smoothness` | `crypto_attack.py smoothness --n n` |

## The ordering

1. `r` scan → `ecdsa-nonce-reuse`.
2. `smoothness --n <order>` → `pohlig-hellman` vs `bsgs`.
3. `Δ` check → `singular_ec`.
4. `#E` count → `smart_attack`.
5. `--nonce-bits`/`bound` check → `hnp-ecdsa`/`hnp`.
6. server validation → invalid curve.
7. none of the above → re-route.

## The two confirmations

`x·G == Q` (curves) · `pow(g, x, p) == h` (fields) — always.
