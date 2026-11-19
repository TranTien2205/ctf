# Per-check deep — each read, the signal, the family, the file, annotated

## The charset checks

| Check | Signal | Family | File |
|---|---|---|---|
| `+/=`/hex/`01`/`.-`/`/` | an encoding | `enc_detect` | `detection.md`,`encoding-*.md` |
| `ADFGVX`/`AB`×5 | a fractionation | `other-ciphers` | `other-ciphers.md`,`playfair-polybius*.md` |
| letters-only | a cipher | the stats | `cipher-identification.md` |
| letters+digits | a partial cipher | the stats | `edge-cases*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` | the format leak | the crib | `known-plaintext*.md` |

## The statistics checks

| Check | Signal | Family | File |
|---|---|---|---|
| IC ~0.066 | monoalpha | `caesar`/`subst`/`atbash` | `cipher-identification.md` |
| IC ~0.038 | polyalpha | `vigenere` | `vigenere-*.md` |
| IC ~0.05-0.066 | transposition | `railfence`/columnar | `railfence-*.md` |
| chi² one min `k` | a shift | `caesar` | `caesar-*.md` |
| chi² flat | a `σ` | `subst` | `subst-*.md` |
| reversed ETAOIN | a reflection | `atbash` | `atbash-*.md` |
| Kasiski `L` | a period | `vigenere --keylen` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN-shaped | a `σ` | `subst` | `subst-*.md` |
| flat freq | polyalpha | `vigenere` | `vigenere-*.md` |
| English counts, scrambled | a `π` | `railfence`/columnar | `railfence-*.md` |
| digraph-structured | a keyed square | `playfair` | `playfair-polybius*.md` |

## The verify checks

| Check | Signal | File |
|---|---|---|
| `enc(pt) == ct` | the transform confirmed | `verify*.md`,`evidence*.md` |
| `pt` language | the decode right | `verify*.md` |
| `flag{`/`CTF{` present | the flag | `evidence*.md` |
| `synt{`/`Pxl{`/`fhpnf{` | a `k`-shift artifact | `caesar-*.md` |
