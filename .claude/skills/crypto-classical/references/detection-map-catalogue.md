# Detection map catalogue — the read → the signal → the family → the file, indexed

## The charset reads

| Read | Signal | Family | File |
|---|---|---|---|
| `+/=` | base64 | `enc_detect` | `encoding-*.md`,`detection.md` |
| `0-9a-f` | hex | `enc_detect` | `encoding-*.md` |
| `01` (8-bit) | binary | `enc_detect` | `encoding-*.md` |
| `.-`/`/` | Morse | `enc_detect` | `encoding-*.md` |
| `AB`×5 | Baconian | `other-ciphers`/`enc_detect` | `other-ciphers.md`,`playfair-polybius*.md` |
| `ADFGVX` | ADFGVX | `other-ciphers` | `other-ciphers.md`,`playfair-polybius*.md` |
| letters-only | a cipher | `cipher_id` | `cipher-identification.md` |
| letters+digits | a partial cipher | `cipher_id` (letters) | `edge-cases*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` | a crib | `known-plaintext` | `known-plaintext*.md` |
| `n = r·c` | a grid | `railfence`/columnar | `railfence-*.md` |
| digraphs | a square | `playfair` | `playfair-polybius*.md` |
| pairs | a grid | `polybius`/adfgvx | `playfair-polybius*.md` |

## The statistics reads

| Read | Signal | Family | File |
|---|---|---|---|
| IC ~0.066 | monoalpha | `caesar`/`subst`/`atbash` | `cipher-identification.md` |
| IC ~0.038 | polyalpha | `vigenere` | `vigenere-*.md` |
| IC ~0.05-0.066 | `π` | `railfence`/columnar | `railfence-*.md` |
| chi² `k` | a shift | `caesar` | `caesar-*.md` |
| chi² flat | a `σ` | `subst` | `subst-*.md` |
| reversed | a reflection | `atbash` | `atbash-*.md` |
| Kasiski `L` | a period | `vigenere` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN-shaped | a `σ` | `subst` | `subst-*.md`,`frequency-analysis*.md` |
| scrambled | a `π` | `railfence`/columnar | `railfence-*.md` |

## The route

`cipher-identification.md` → the family → `classical_solve`.
