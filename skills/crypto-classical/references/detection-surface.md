# Detection surface — the observable → the read

## The `ct` surface

| Observable | The read |
|---|---|
| the charset | cipher vs encoding — `+/=`/hex/`01`/`.-` → `enc_detect` |
| the length | a grid shape (`n = r·c`) → transposition |
| the format | `flag{`/`CTF{`/`SNT{`/`synt{` positions |
| a name | "caesar"/"vigenere"/"playfair" → the decoder |
| a key word | "key"/"keyword" → `vigenere`/`subst` |
| "rail"/"fence"/"columns" | → `railfence`/columnar |
| "shifted"/"rot" | → `caesar` |

## The statistics surface

| Observable | The read |
|---|---|
| IC ~0.066 | monoalpha — `caesar`/`subst`/`atbash` |
| IC ~0.038 | polyalpha — `vigenere` |
| IC ~0.05-0.066 | transposition — `railfence`/columnar |
| chi² one min | `caesar` — the `k` |
| chi² flat | `subst` — a non-cyclic `σ` |
| Kasiski `L` | `vigenere --keylen` |
| ETAOIN-shaped | a `σ` — `σ(E)` is the top letter |
| reversed ETAOIN | `atbash` |

## The route

`cipher-identification.md` → the family → `classical_solve <family>`.
