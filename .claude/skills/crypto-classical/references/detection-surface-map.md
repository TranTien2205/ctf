# Detection surface map — the `ct` shape → the family → the file

## The `ct` shape → the family → the file

| Shape | The family | The file |
|---|---|---|
| letters-only | a cipher | `cipher-identification.md` |
| `+/=`/hex/`01`/`.-`/`/` | an encoding | `encoding-*.md` |
| `ADFGVX`/`AB`×5 | a fractionation | `other-ciphers.md`,`playfair-polybius*.md` |
| letters+digits | a partial cipher | `edge-cases*.md` |
| mixed case | a Baconian/binary channel | `edge-cases*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | the crib | `known-plaintext*.md` |
| `n = r·c` | a grid | `railfence-*.md`,`transposition-variants*.md` |
| scrambled letters | a `π` | `railfence-*.md` |
| ETAOIN-not-English | a `σ` | `subst-*.md` |
| flat freq | a polyalpha | `vigenere-*.md` |
| reversed ETAOIN | a reflection | `atbash-*.md` |
| digraphs | a square | `playfair-polybius*.md` |

## The statistics → the family → the file

| Statistic | The family | The file |
|---|---|---|
| IC ~0.066 | monoalpha | `cipher-identification.md` |
| IC ~0.038 | polyalpha | `vigenere-*.md` |
| IC ~0.05-0.066 | `π` | `railfence-*.md` |
| chi² `k` | `caesar` | `caesar-*.md` |
| chi² flat | `subst` | `subst-*.md` |
| reversed | `atbash` | `atbash-*.md` |
| Kasiski `L` | `vigenere` | `vigenere-*.md`,`key-length*.md` |

## The route

`cipher-identification.md` → the family → `classical_solve`.
