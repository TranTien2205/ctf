# Probe map deep — the read → the signal → the family → the file

| Read | Signal | Family | File |
|---|---|---|---|
| `cipher_id` IC~0.066 | monoalpha | `caesar`/`subst`/`atbash` | `cipher-identification.md` |
| `cipher_id` IC~0.038 | polyalpha | `vigenere` | `vigenere-*.md` |
| `cipher_id` IC~0.05 | transposition | `railfence`/columnar | `railfence-*.md` |
| `cipher_id` chi² `k` | a shift | `caesar` | `caesar-*.md` |
| `cipher_id` chi² flat | a `σ` | `subst` | `subst-*.md` |
| `cipher_id` reversed | a reflection | `atbash` | `atbash-*.md` |
| `cipher_id` Kasiski `L` | a period | `vigenere --keylen` | `vigenere-*.md` |
| scrambled letters | a `π` | `railfence`/columnar | `railfence-*.md` |
| `+/=`/hex/`01` | an encoding | `enc_detect` | `encoding-vs-cipher.md` |
| a name | the decoder | the family | `other-ciphers.md` |
| `flag{` positions | a crib | the transform | `known-plaintext.md` |
| `n = r·c` | a grid | `railfence`/route | `railfence-*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify.md`,`evidence.md`.
