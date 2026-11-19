# Detection map — the read order → the signal → the file

## The artifact reads

| Read | The file |
|---|---|
| `ls`/`file`/`xxd` | `detection*.md`,`detection-surface*` |
| `RSA.importKey` | `parameter-sheet.md`,`detection*.md` |
| `re.findall` | `detection*.md`,`probe-catalogue.md` |
| `keygen`/`chal` grep | `detection*.md`,`detection-catalogue*` |
| `crypto_attack.py list` | `detection*.md`,`attack-table*` |

## The arithmetic reads

| `n`,`e`,`c` counts | `detection*.md`,`detection-matrix*` |
| `e` size | `detection*.md`,`per-signal.md` |
| `gcd(e,phi)` | `detection*.md`,`eth-root*.md` |
| `n` square/prime | `detection*.md`,`edge-cases*` |
| `m^e` vs `n` | `detection*.md`,`small-e-root*.md` |

## The route reads

| `attack-table.md` row | `attack-table*.md`,`decision-table.md` |
| `per-bound.md` bound | `per-bound.md`,`lattice-bounds.md` |
| `crypto_attack.py <id>` | `workflow*.md`,`payload-*` |

## The verify

`pow(m,e,n)==c` / `p*q==n`.
