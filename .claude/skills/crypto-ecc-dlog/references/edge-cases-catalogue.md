# Edge cases catalogue — the disguised limits → the files

## The format edge cases → files

| Case | Files |
|---|---|
| DER/ASN.1 sig | `edge-cases-deep.md`,`edge-cases*.md` |
| compressed `Q` | `edge-cases-deep.md` |
| `z` as message | `edge-cases-deep.md`,`per-check*.md` |
| mixed reuse+bias | `edge-cases-deep.md` |

## The math edge cases → files

| Case | Files |
|---|---|
| `x` edge of bound | `edge-cases*.md`,`per-boundary*.md` |
| `ord` cofactor | `edge-cases-deep.md`,`per-check*.md` |
| `Δ`/`#E` near-miss | `edge-cases*.md`,`per-check*.md` |
| `k` edge of `B` | `edge-cases-deep.md`,`hnp-*.md` |

## The oracle edge cases → files

| Case | Files |
|---|---|
| partial validation | `invalid-curve-deep.md`,`edge-cases*.md` |
| rate-limited oracle | `edge-cases-deep.md`,`recon-order*.md` |
| error-oracle | `edge-cases-deep.md`,`invalid-curve-deep.md` |

## The class edge cases → files

| Case | Files |
|---|---|
| no `Q`/`h` to verify | `edge-cases-deep.md`,`class-boundary*.md` |
| flag-not-scalar shape | `edge-cases-deep.md`,`evidence*.md` |
