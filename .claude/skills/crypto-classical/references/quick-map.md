# Quick map — the signal → the command → the bound

| Signal | Command | Bound |
|---|---|---|
| IC~0.066, one chi² min | `classical_solve caesar --text` | a `k` |
| IC~0.066, flat chi² | `classical_solve subst --text` | a `σ` |
| IC~0.038, `L` | `classical_solve vigenere --text --keylen L` | an `L` |
| scrambled letters | `classical_solve railfence --text` | a depth |
| reversed alphabet | `classical_solve atbash --text` | the reflection |
| `+/=`/hex/`01` | `enc_detect` | an encoding |
| a name in the text | `classical_solve <family>`/a script | the decoder |
| `flag{` positions | the format leak | the transform |

## The verify

`pt` language + `enc(pt)=ct`.
