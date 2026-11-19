# Detection index map — read → family → files

## `r` reads → nonce family → files

| Read | Family | Files |
|---|---|---|
| dup `r` | nonce | `per-family-nonce.md`,`ecdsa-nonce-reuse*.md` |
| `k < B` | nonce | `per-family-nonce.md`,`hnp-ecdsa*.md` |
| `(t,u)` | nonce | `per-family-nonce.md`,`hnp*.md` |

## `ord`/`h` reads → dlog family → files

| Read | Family | Files |
|---|---|---|
| smooth | dlog | `per-family-dlog.md`,`pohlig-hellman*.md` |
| bounded `x` | dlog | `per-family-dlog.md`,`bsgs*.md` |
| `ord` ? | dlog | `per-family-dlog.md`,`smoothness*.md` |

## `Δ`/`#E`/validation reads → defect family → files

| Read | Family | Files |
|---|---|---|
| `Δ == 0` | defect | `per-family-curve-defect.md`,`singular-ec*.md` |
| `#E == p` | defect | `per-family-curve-defect.md`,`smart-attack*.md` |
| no validation | defect | `per-family-curve-defect.md`,`invalid-curve*.md` |

## The route files

`cipher-identification.md`,`detection-matrix.md`,`detection-playbook*.md`.

## The close files

`verify*.md`,`evidence*.md`,`field-notes-index.md`,`negative-results*.md`.
