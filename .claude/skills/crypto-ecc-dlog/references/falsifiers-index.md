# Falsifiers index — the kill conditions → the files

## The nonce kills → files

| Kill | Files |
|---|---|
| no dup `r` | `falsifiers*.md`,`per-falsifier.md`,`negative-results*.md` |
| `d·G ≠ Q` | `falsifiers*.md`,`troubleshoot*.md` |

## The lattice kills → files

| Kill | Files |
|---|---|
| `d·G ≠ Q` at count | `falsifiers*.md`,`hnp-ecdsa-deep.md` |
| `k` outlier | `falsifiers*.md`,`per-check*.md` |

## The dlog kills → files

| Kill | Files |
|---|---|
| factor > 2⁴⁰ | `falsifiers*.md`,`smoothness-deep.md` |
| `g^x ≠ h` | `falsifiers*.md`,`pohlig-hellman-deep.md` |
| `ord` > 2⁴⁴ | `falsifiers*.md`,`bsgs-deep.md` |
| `h ∉ <g>` | `falsifiers*.md`,`per-check*.md` |

## The defect kills → files

| Kill | Files |
|---|---|
| `#E ≠ p` | `falsifiers*.md`,`smart-attack-deep.md` |
| `Δ ≠ 0` | `falsifiers*.md`,`singular-ec-deep.md` |
| validated `P` | `falsifiers*.md`,`invalid-curve-deep.md` |

## The class kill → files

| Kill | Files |
|---|---|
| `x·G ≠ Q` | `falsifiers*.md`,`class-boundary*.md` |

## The record → files

`negative-results*.md` `attempts` `decide.py`.
