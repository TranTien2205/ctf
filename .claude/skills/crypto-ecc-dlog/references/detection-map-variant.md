# Detection map variant — observation → route → file, the table edition

## The primary observations → route

| Observe | Route |
|---|---|
| sigs | nonce gate |
| `h = g^x` | dlog gate |
| `p a b` | defect gate |
| oracle | validation probe |

## The secondary observations → route

| Observe | Route |
|---|---|
| `r` dup | `ecdsa-nonce-reuse` |
| `k` bound | `hnp-ecdsa` |
| `(t,u)` | `hnp` |
| smooth `ord` | `pohlig-hellman` |
| bounded `x` | `bsgs` |
| `Δ == 0` | `singular_ec` |
| `#E == p` | `smart_attack` |
| unvalidated | invalid curve |

## The files per observation → per route

| Observation | Route files |
|---|---|
| sigs | `per-family-nonce.md`,`per-attack-*.md` |
| `h = g^x` | `per-family-dlog.md`,`per-attack-*.md` |
| `p a b` | `per-family-curve-defect.md`,`per-attack-*.md` |
| oracle | `per-family-curve-defect.md`,`invalid-curve-deep.md` |

## The close files

`verify*` `evidence*` `field-notes-*` `falsifiers*` `negative-results*`
`decide.py`.
