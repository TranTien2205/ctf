# Detection surface index — the observable → the read → the file, indexed

## The `ct` shape reads

| Observable | The read | The files |
|---|---|---|
| the charset | cipher vs encoding | `detection.md`,`encoding-*.md`,`detection-checklist*.md` |
| the length | `n = r·c` | `railfence-*.md`,`transposition-variants*.md` |
| the format | `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | `known-plaintext*.md`,`case-studies*.md` |
| a cipher name | the decoder | `other-ciphers*.md`,`lead-grammar*.md` |
| a key word | `vigenere`/`subst` | `vigenere-*.md`,`subst-*.md` |
| "rail"/"fence"/"columns" | a `π` | `railfence-*.md` |
| "shifted"/"rot"/"k=N" | a `k` | `caesar-*.md` |
| "reversed"/"mirrored" | a reflection | `atbash-*.md` |
| digraphs/pairs/`ADFGVX`/`AB`×5 | a fractionation | `playfair-polybius*.md`,`other-ciphers.md` |
| mixed case | a Baconian/binary channel | `edge-cases*.md` |
| letters+digits | a partial cipher | `edge-cases*.md` |

## The statistics reads

| Observable | The read | The files |
|---|---|---|
| IC ~0.066 | monoalpha | `cipher-identification.md`,`detection-deep.md` |
| IC ~0.038 | polyalpha | `vigenere-*.md` |
| IC ~0.05-0.066 | transposition | `railfence-*.md` |
| chi² one min | `caesar` | `caesar-*.md` |
| chi² flat | `subst` | `subst-*.md` |
| reversed ETAOIN | `atbash` | `atbash-*.md` |
| Kasiski `L` | `vigenere` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN-shaped | `subst` | `subst-*.md`,`frequency-analysis*.md` |
| flat freq | `vigenere` | `vigenere-*.md` |
| scrambled | `π` | `railfence-*.md` |

## The route files

`cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md`,
`workflow*.md`,`payload-dictionary*.md`.
