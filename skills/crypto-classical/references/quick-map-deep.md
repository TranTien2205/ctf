# Quick map deep — the signal → the command → the bound, annotated

| Signal | Command | Bound | The close |
|---|---|---|---|
| IC~0.066, chi² `k` | `classical_solve caesar --text` | a `k` in 25 | no `k` → `subst`/`π` |
| IC~0.066, reversed | `classical_solve atbash --text` | the reflection | garbage → `subst` |
| IC~0.066, flat | `classical_solve subst --text` | a `σ` | no language → `π` |
| IC~0.038, `L` | `classical_solve vigenere --text --keylen L` | an `L` + key | no `L` → `subst`/`π`/other |
| IC~0.05, scrambled | `classical_solve railfence --text` | a depth `r` | no depth → a different `π` or `σ` |
| `+/=`/hex/`01`/`.-` | `enc_detect` | an encoding | letters-only → a cipher |
| `ADFGVX`/`AB`×5 | `other-ciphers`/script | the decoder | the `cipher_id` shape |
| a name | `other-ciphers.md` → a script | the decoder | the family shape |
| `flag{` positions | `known-plaintext.md` → the crib | the transform | the `flag{` decode |
| `n = r·c` | `railfence`/columnar/route | a `w`/`π` | no `π` → `σ` |
| `SNT{`/`synt{`/`Pxl{`/`fhpnf{` | decode the format | `k` | a `k`-shift artifact |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
