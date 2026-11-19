# Detection catalogue variant — signals → routes → files, the matrix edition

## The signature rows

| Signal | Route | Files |
|---|---|---|
| `r` dup | `ecdsa-nonce-reuse` | `per-attack-ecdsa-nonce-reuse.md` |
| `k < B` | `hnp-ecdsa` | `per-attack-hnp-ecdsa.md` |
| `(t,u)` | `hnp` | `per-attack-hnp.md` |
| deterministic | RFC 6979 | `edge-cases-deep.md` |
| `k` ts-seeded | `hnp-ecdsa --nonce-bound` | `scenarios*.md` |

## The dlog rows

| Signal | Route | Files |
|---|---|---|
| `ord` smooth | `pohlig-hellman` | `per-attack-pohlig-hellman.md` |
| `x` bounded | `bsgs` | `per-attack-bsgs.md` |
| `ord` ? | `smoothness` | `per-attack-smoothness.md` |
| `2q` order | dead | `boundary-cases*.md` |

## The defect rows

| Signal | Route | Files |
|---|---|---|
| `#E == p` | `smart_attack` | `per-attack-smart.md` |
| `Δ == 0` | `singular_ec` | `per-attack-singular.md` |
| unvalidated `P` | invalid curve | `per-attack-invalid-curve.md` |

## The format rows

| Signal | Route | Files |
|---|---|---|
| DER sig | normalize | `edge-cases-deep.md` |
| compressed `Q` | decompress | `edge-cases-deep.md` |
| `z` message | hash first | `edge-cases-deep.md` |
| `jwt` | nonce | `scenarios*.md` |

## The close rows

| Signal | Route | Files |
|---|---|---|
| scalar | verify | `verify*.md` |
| flag | record | `evidence*.md` |
| no match | falsifier | `falsifiers*.md`,`negative-results*.md` |
