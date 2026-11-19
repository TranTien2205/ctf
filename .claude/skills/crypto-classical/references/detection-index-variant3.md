# Detection index variant 3 — the reads, by the file they route to

## The `detection*.md` reads

| Read | The files |
|---|---|
| `cipher_id` | `detection.md`,`detection-deep.md`,`cipher-identification.md` |
| `enc_detect` | `encoding-*.md`,`detection.md` |
| the charset | `detection.md`,`detection-checklist*.md`,`detection-surface*.md` |

## The `cipher-identification.md` reads

| Read | The files |
|---|---|
| the tuple → the family | `cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md` |
| the family → the command | `payload-dictionary*.md`,`workflow-map.md` |

## The family reads → the `*-deep.md` files

| Family | The files |
|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md`,`shift-variants*.md` |
| `subst` | `subst-*.md`,`monoalphabetic-variants*.md`,`language-scoring*.md` |
| `vigenere` | `vigenere-*.md`,`polyalphabetic-variants*.md`,`beaufort-autokey*.md`,`key-length*.md` |
| `railfence` | `railfence-*.md`,`transposition-variants*.md` |
| named others | `other-ciphers*.md`,`playfair-polybius*.md` |
| encoding | `encoding-*.md` |

## The close reads → the close files

| Read | The files |
|---|---|
| the verify | `verify*.md`,`evidence*.md` |
| the falsifier | `falsifiers*.md`,`per-falsifier*.md` |
| the record | `field-notes-catalogue.md`,`negative-*.md` |
| the escalate | `falsifiers*.md` — `decide.py` |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`,
`summary*.md`,`closing-index.md`.
