# Detection index map deep — the read → the signal → the file, fully indexed

## The `cipher_id` reads → the files

| Read | Signal | The files |
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

## The `ct`-shape reads → the files

| Read | Signal | The files |
|---|---|---|
| `+/=`/hex/`01`/`.-`/`/` | an encoding | `encoding-*.md`,`detection.md` |
| `ADFGVX`/`AB`×5 | a fractionation | `other-ciphers*.md`,`playfair-polybius*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | a crib | `known-plaintext*.md` |
| `n = r·c` | a grid | `railfence-*.md`,`transposition-variants*.md` |
| a cipher name | a decoder | `other-ciphers*.md`,`lead-grammar*.md` |
| a "key"/"keyword" | a keyed cipher | `vigenere-*.md`,`subst-*.md` |
| "rail"/"fence"/"columns" | a `π` | `railfence-*.md` |
| mixed case | a channel | `edge-cases*.md` |
| letters+digits | a partial cipher | `edge-cases*.md` |

## The route files

`cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md`,
`workflow*.md`,`payload-dictionary*.md`.
