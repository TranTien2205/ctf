# Detection surface deep — the observable → the read, annotated

## The `ct` surface — the shape reads

| Observable | The read | The family |
|---|---|---|
| the charset | cipher vs encoding — `+/=`/hex/`01`/`.-`/`ADFGVX` | `enc_detect` |
| the length | `n = r·c` → a grid | `railfence`/columnar/route |
| the format | `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | the crib |
| a name | "caesar"/"vigenere"/"playfair"/"adfgvx" | `other-ciphers.md` |
| a key word | "key"/"keyword"/"lemon" | `vigenere`/`subst` |
| "rail"/"fence"/"columns" | a `π` shape | `railfence`/columnar |
| "shifted"/"rot"/"k=N" | a `k` | `caesar` |
| "reversed"/"mirrored" | a reflection | `atbash` |
| digraphs/pairs/`ADFGVX` | a fractionation | `playfair-polybius` |

## The statistics surface — the `cipher_id` reads

| Observable | The read | The family |
|---|---|---|
| IC ~0.066 | monoalpha | `caesar`/`subst`/`atbash` |
| IC ~0.038 | polyalpha | `vigenere` |
| IC ~0.05-0.066 | transposition | `railfence`/columnar |
| chi² one min | a `k` | `caesar` |
| chi² flat | a `σ` | `subst` |
| reversed ETAOIN | a reflection | `atbash` |
| Kasiski `L` | a period | `vigenere --keylen` |
| ETAOIN-shaped | a `σ` | `subst` |
| flat freq | polyalpha | `vigenere` |
| English counts, scrambled | a `π` | `railfence` |

## The route

`cipher-identification.md` → the family → `classical_solve`.
