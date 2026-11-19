# Detection playbook map — the discriminate → the family → the file

## The charset playbook → the file

| Charset | The family | The files |
|---|---|---|
| `+/=`/hex/`01`/`.-`/`/` | `enc_detect` | `encoding-*.md`,`detection.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers` | `other-ciphers*.md`,`playfair-polybius*.md` |
| letters-only | `cipher_id` | `cipher-identification.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | the crib | `known-plaintext*.md` |
| `n = r·c` | a grid | `railfence-*.md` |

## The `cipher_id` playbook → the file

| Read | The family | The files |
|---|---|---|
| IC ~0.066 | monoalpha | `caesar-*.md`,`subst-*.md`,`atbash-*.md` |
| IC ~0.038 | polyalpha | `vigenere-*.md` |
| IC ~0.05 | `π` | `railfence-*.md` |
| chi² `k` | `caesar` | `caesar-*.md` |
| chi² flat | `subst` | `subst-*.md` |
| reversed | `atbash` | `atbash-*.md` |
| Kasiski `L` | `vigenere` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN | `subst` | `subst-*.md` |
| scrambled | `π` | `railfence-*.md` |

## The route files

`cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md`,
`payload-dictionary*.md`.
