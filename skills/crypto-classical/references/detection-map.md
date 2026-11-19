# Detection map — the read → the signal → the file

| Read | Signal | File |
|---|---|---|
| the charset | `+/=`/hex/`01`/`.-` | `detection.md`,`class-boundary.md` |
| `cipher_id` IC | ~0.066 mono / ~0.038 poly | `detection*.md`,`cipher-identification.md` |
| `cipher_id` chi² | one min `k` / flat | `caesar-*.md`,`subst-*.md` |
| `cipher_id` Kasiski | an `L` | `vigenere-*.md` |
| the frequency | ETAOIN / reversed / flat | `subst-*.md`,`atbash-*.md` |
| the format | `flag{`/`CTF{`/`SNT{` | `detection.md`,`case-studies*.md` |
| a name | the decoder | `other-ciphers.md` |
| the length | a grid `r·c` | `railfence-*.md` |

## The route

`cipher-identification.md` — the tuple → the family → `classical_solve`.
