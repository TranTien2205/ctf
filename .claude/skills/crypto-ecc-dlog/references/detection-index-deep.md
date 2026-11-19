# Detection index deep — every read → the file that owns it

## The nonce reads

| Read | File |
|---|---|
| `r` dedupe | `detection*.md`,`per-family-nonce.md`,`per-check.md` |
| `k < B` bound | `hnp-ecdsa-deep.md`,`per-boundary.md` |
| `(t,u)` derivation | `hnp-deep.md`,`mechanism-deep.md` |
| sig count | `hnp-ecdsa-deep.md`,`per-boundary.md`,`per-check.md` |

## The dlog reads

| Read | File |
|---|---|
| `ord` factorization | `smoothness-deep.md`,`per-family-dlog.md` |
| `x` bound | `bsgs-deep.md`,`per-boundary.md` |
| `h ∈ <g>` | `per-check.md`,`pohlig-hellman-deep.md` |

## The defect reads

| Read | File |
|---|---|
| `Δ mod p` | `singular-ec-deep.md`,`per-check.md` |
| `#E` count | `smart-attack-deep.md`,`per-check.md` |
| point validation | `invalid-curve-deep.md`,`edge-cases-deep.md` |

## The route reads

| Read | File |
|---|---|
| tuple → attack | `cipher-identification.md`,`detection-matrix.md` |
| attack → command | `payload-dictionary*.md`,`per-attack-*.md` |
| command → verify | `verify*.md`,`evidence*.md` |
| fail → falsifier | `falsifiers*.md`,`per-falsifier.md` |
| fail → record | `negative-results*.md`,`field-notes-index.md` |

## The index reads

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`.
