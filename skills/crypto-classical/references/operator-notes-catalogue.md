# Operator notes catalogue — the field-guide, indexed

## The order

`cipher_id` → `cipher-identification` → `classical_solve <family>` →
`evidence` → `field-notes` — `workflow*.md`.

## The tools — the measured interfaces

| Tool | The flags | The file |
|---|---|---|
| `tools/cipher_id.py` | `--text`,`--selftest` | `preconditions.md` |
| `tools/classical_solve.py` | `{caesar,vigenere,subst,atbash,railfence}`,`--text`,`--keylen`,`--key`,`--restarts`,`--iters`,`--selftest` | `payload-dictionary*.md` |
| `tools/enc_detect.py` | `data`,`--file`,`--selftest` | `encoding-*.md` |
| a script / dcode.fr | the named others | `other-ciphers.md` |

## The signals → the families

| Signal | The family | The file |
|---|---|---|
| IC ~0.066 | monoalpha | `cipher-identification.md` |
| IC ~0.038 | polyalpha | `vigenere-*.md` |
| chi² `k` | `caesar` | `caesar-*.md` |
| chi² flat | `subst` | `subst-*.md` |
| reversed | `atbash` | `atbash-*.md` |
| Kasiski `L` | `vigenere` | `vigenere-*.md` |
| scrambled | `π` | `railfence-*.md` |
| `+/=`/hex | `enc_detect` | `encoding-*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.

## The record

`post-probe` · `classify_solve.py` · `../field-notes.md` · `knowledge/attempts/`.
