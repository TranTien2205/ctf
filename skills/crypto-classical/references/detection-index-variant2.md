# Detection index variant 2 — the reads, fully indexed, the matrix edition

## The IC reads → the family files

| IC | The family | The files |
|---|---|---|
| ~0.066 | monoalpha — `caesar`/`subst`/`atbash` | `cipher-identification.md`,`caesar-*.md`,`subst-*.md`,`atbash-*.md` |
| ~0.038 | polyalpha — `vigenere` | `vigenere-*.md` |
| ~0.05-0.066 | `π` — `railfence`/columnar | `railfence-*.md` |

## The chi² reads → the family files

| chi² | The family | The files |
|---|---|---|
| one min `k` | `caesar` | `caesar-*.md` |
| flat | `subst` | `subst-*.md` |
| reversed | `atbash` | `atbash-*.md` |

## The Kasiski reads → the family files

| Kasiski | The family | The files |
|---|---|---|
| an `L` | `vigenere` | `vigenere-*.md`,`key-length*.md` |
| no `L` | `subst`/`π`/autokey | `subst-*.md`,`railfence-*.md`,`beaufort-autokey*.md` |

## The freq reads → the family files

| Freq | The family | The files |
|---|---|---|
| ETAOIN | `subst` | `subst-*.md`,`frequency-analysis*.md` |
| reversed | `atbash` | `atbash-*.md` |
| flat | `vigenere` | `vigenere-*.md` |
| scrambled | `π` | `railfence-*.md` |

## The charset reads → the family files

| Charset | The family | The files |
|---|---|---|
| `+/=`/hex/`01`/`.-` | `enc_detect` | `encoding-*.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers`/`playfair-polybius*` | `other-ciphers*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` | the crib | `known-plaintext*.md` |
| letters-only | `cipher_id` | `cipher-identification.md` |
| letters+digits | a partial cipher | `edge-cases*.md` |
| mixed case | a channel | `edge-cases*.md` |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`.
