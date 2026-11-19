# Detection index map — the read → the signal → the file, indexed

## The `cipher_id` reads

| Read | Signal | File |
|---|---|---|
| IC ~0.066 | monoalpha | `cipher-identification.md`,`caesar-*.md`,`subst-*.md`,`atbash-*.md` |
| IC ~0.038 | polyalpha | `vigenere-*.md` |
| IC ~0.05-0.066 | `π` | `railfence-*.md` |
| chi² `k` | a shift | `caesar-*.md` |
| chi² flat | a `σ` | `subst-*.md` |
| reversed | a reflection | `atbash-*.md` |
| Kasiski `L` | a period | `vigenere-*.md`,`key-length*.md` |
| ETAOIN | a `σ` | `subst-*.md`,`frequency-analysis*.md` |
| scrambled | a `π` | `railfence-*.md` |
| digraphs | a square | `playfair-polybius*.md` |

## The `ct`-shape reads

| Read | Signal | File |
|---|---|---|
| `+/=`/hex/`01`/`.-` | an encoding | `encoding-*.md` |
| `ADFGVX`/`AB`×5 | a fractionation | `other-ciphers*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | a crib | `known-plaintext*.md` |
| `n = r·c` | a grid | `railfence-*.md` |
| a name | a decoder | `other-ciphers*.md`,`lead-grammar*.md` |
| a keyword | a keyed cipher | `vigenere-*.md`,`subst-*.md` |
| mixed case | a channel | `edge-cases*.md` |
| letters+digits | a partial cipher | `edge-cases*.md` |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`,
`summary*.md`,`closing-index.md`.
