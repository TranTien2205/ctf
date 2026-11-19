# Detection index catalogue deep — the reads, the files, fully indexed

## The `cipher_id` reads → the files

| Read | The files |
|---|---|
| IC ~0.066 | `cipher-identification.md`,`caesar-*.md`,`subst-*.md`,`atbash-*.md` |
| IC ~0.038 | `vigenere-*.md` |
| IC ~0.05 | `railfence-*.md` |
| chi² `k` | `caesar-*.md` |
| chi² flat | `subst-*.md` |
| reversed | `atbash-*.md` |
| Kasiski `L` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN | `subst-*.md`,`frequency-analysis*.md` |
| flat freq | `vigenere-*.md` |
| scrambled | `railfence-*.md` |
| digraphs | `playfair-polybius*.md` |

## The `ct`-shape reads → the files

| Read | The files |
|---|---|
| `+/=`/hex/`01`/`.-`/`/` | `encoding-*.md`,`detection.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers*.md`,`playfair-polybius*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | `known-plaintext*.md` |
| `n = r·c` | `railfence-*.md`,`transposition-variants*.md` |
| a cipher name | `other-ciphers*.md`,`lead-grammar*.md` |
| a "key"/"keyword" | `vigenere-*.md`,`subst-*.md` |
| "rail"/"fence"/"columns" | `railfence-*.md` |
| mixed case | `edge-cases*.md` |
| letters+digits | `edge-cases*.md` |

## The route files

`cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md`,
`workflow*.md`,`payload-dictionary*.md`.

## The close files

`verify*.md`,`evidence*.md`,`falsifiers*.md`,`negative-*.md`.

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`,
`summary*.md`,`closing-index.md`.
