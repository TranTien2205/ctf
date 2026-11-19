# Detection surface catalogue — the observable → the read, fully indexed

## The `ct` shape surface

| Observable | The read | The files |
|---|---|---|
| the charset | cipher vs encoding | `detection.md`,`encoding-*.md`,`detection-surface*.md` |
| the length | `n = r·c` → a grid | `railfence-*.md`,`transposition-variants*.md` |
| the format | `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | `known-plaintext*.md`,`detection.md` |
| a cipher name | the decoder | `other-ciphers.md`,`lead-grammar*.md` |
| a key word | `vigenere`/`subst` | `vigenere-*.md`,`subst-*.md` |
| "rail"/"fence"/"columns" | a `π` | `railfence-*.md` |
| "shifted"/"rot"/"k=N" | a `k` | `caesar-*.md` |
| "reversed"/"mirrored" | a reflection | `atbash-*.md` |
| digraphs/pairs/`ADFGVX`/`AB`×5 | a fractionation/Baconian | `playfair-polybius*.md`,`other-ciphers.md` |

## The statistics surface

| Observable | The read | The files |
|---|---|---|
| IC ~0.066 | monoalpha | `cipher-identification.md`,`detection-deep.md` |
| IC ~0.038 | polyalpha | `vigenere-*.md` |
| IC ~0.05-0.066 | transposition | `railfence-*.md` |
| chi² one min | `caesar` | `caesar-*.md` |
| chi² flat | `subst` | `subst-*.md` |
| reversed ETAOIN | `atbash` | `atbash-*.md` |
| Kasiski `L` | `vigenere --keylen` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN-shaped | `subst` | `subst-*.md`,`frequency-analysis*.md` |
| flat freq | `vigenere` | `vigenere-*.md` |
| English counts, scrambled | `π` | `railfence-*.md` |
| digraph-structured | `playfair` | `playfair-polybius*.md` |

## The route

`cipher-identification.md` → the family → `classical_solve` — `workflow*.md`.
