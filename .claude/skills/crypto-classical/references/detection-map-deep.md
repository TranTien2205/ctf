# Detection map deep — the read → the signal → the family → the file

## The charset reads

| Read | Signal | Family | File |
|---|---|---|---|
| `+/=` (base64) | 64-char alphabet | `enc_detect` | `detection.md`,`encoding-vs-cipher.md` |
| `0-9a-f` | hex | `enc_detect` | `detection.md` |
| `01` (8-bit) | binary | `enc_detect` | `detection.md` |
| `.-`/`/` | Morse | `enc_detect` | `detection.md` |
| `AB`×5 | Baconian | `enc_detect` | `other-ciphers.md` |
| `ADFGVX` | ADFGX | `other-ciphers` | `other-ciphers.md` |
| letters-only | a cipher | the stats | `cipher-identification.md` |
| letters+digits | a partial cipher | the stats | `edge-cases.md` |

## The statistics reads

| Read | Signal | Family | File |
|---|---|---|---|
| IC ~0.066 | monoalpha | `caesar`/`subst`/`atbash` | `cipher-identification.md` |
| IC ~0.038 | polyalpha | `vigenere` | `vigenere-*.md` |
| IC ~0.05-0.066 | transposition | `railfence`/columnar | `railfence-*.md` |
| chi² one min `k` | a shift | `caesar` | `caesar-*.md` |
| chi² flat | a `σ` | `subst` | `subst-*.md` |
| chi² reversed | a reflection | `atbash` | `atbash-*.md` |
| Kasiski `L` | the period | `vigenere --keylen` | `vigenere-*.md` |
| ETAOIN-shaped | a `σ` | `subst` | `subst-*.md` |
| reversed ETAOIN | a reflection | `atbash` | `atbash-*.md` |
| flat freq | polyalpha | `vigenere` | `vigenere-*.md` |
| English counts, scrambled | a `π` | `railfence`/columnar | `railfence-*.md` |

## The context reads

| Read | Signal | Family | File |
|---|---|---|---|
| a cipher name | the decoder | the family | `other-ciphers.md` |
| a "key"/"keyword" | a keyed cipher | `vigenere`/`subst` | `vigenere-*.md`,`subst-*.md` |
| "rail"/"fence"/"columns" | a `π` | `railfence`/columnar | `railfence-*.md` |
| `flag{`/`CTF{` | the format leak | the crib | `known-plaintext.md` |
| `n = r·c` | a grid | `railfence`/route | `railfence-*.md` |
