# Detection index — the reads, indexed by family

## Nonce family reads

| Read | Attack | Files |
|---|---|---|
| `r` dup | `ecdsa-nonce-reuse` | `per-family-nonce.md`,`ecdsa-nonce-reuse-deep.md` |
| `k < B` | `hnp-ecdsa` | `per-family-nonce.md`,`hnp-ecdsa-deep.md` |
| `(t,u)` leak | `hnp` | `per-family-nonce.md`,`hnp-deep.md` |

## Dlog family reads

| Read | Attack | Files |
|---|---|---|
| smooth `ord` | `pohlig-hellman` | `per-family-dlog.md`,`pohlig-hellman-deep.md` |
| bounded `x` | `bsgs` | `per-family-dlog.md`,`bsgs-deep.md` |
| `ord` unknown | `smoothness` | `per-family-dlog.md`,`smoothness-deep.md` |

## Defect family reads

| Read | Attack | Files |
|---|---|---|
| `#E == p` | `smart_attack` | `per-family-curve-defect.md`,`smart-attack-deep.md` |
| `Δ == 0` | `singular_ec` | `per-family-curve-defect.md`,`singular-ec-deep.md` |
| no validation | invalid curve | `per-family-curve-defect.md`,`invalid-curve-deep.md` |

## The route files

`cipher-identification.md`,`detection-matrix.md`,`detection-playbook.md`,
`per-family-*.md`.
