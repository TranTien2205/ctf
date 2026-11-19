# Per-check catalogue — every check, indexed

## The charset checks

| Check | File |
|---|---|
| `+/=`/hex/`01`/`.-`/`/` | `detection.md`,`encoding-*.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers.md`,`playfair-polybius*.md` |
| letters-only | `cipher-identification.md` |
| letters+digits | `edge-cases*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | `known-plaintext*.md` |

## The statistics checks

| Check | File |
|---|---|
| IC ~0.066 | `cipher-identification.md`,`detection-deep.md` |
| IC ~0.038 | `vigenere-*.md`,`detection-deep.md` |
| IC ~0.05-0.066 | `railfence-*.md` |
| chi² `k` | `caesar-*.md` |
| chi² flat | `subst-*.md` |
| reversed | `atbash-*.md` |
| Kasiski `L` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN-shaped | `subst-*.md`,`frequency-analysis*.md` |
| flat freq | `vigenere-*.md` |
| scrambled | `railfence-*.md` |
| digraphs | `playfair-polybius*.md` |

## The verify checks

| Check | File |
|---|---|
| `enc(pt) == ct` | `verify*.md` |
| `pt` language | `verify*.md` |
| `flag{`/`CTF{` | `evidence*.md` |
| `synt{`/`Pxl{`/`fhpnf{` | `caesar-*.md` |
