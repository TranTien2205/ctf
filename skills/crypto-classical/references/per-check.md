# Per-check — each read, the signal, the family, the file

## The charset

| Check | Signal | Family | File |
|---|---|---|---|
| `+/=`/hex/`01`/`.-`/`/` | an encoding | `enc_detect` | `detection.md` |
| letters-only, no spaces | a cipher | the stats | `cipher-identification.md` |
| `flag{`/`CTF{`/`SNT{` | the format leak | a cipher | `case-studies-deep.md` |

## The statistics

| Check | Signal | Family | File |
|---|---|---|---|
| IC ~0.066, chi² `k` | a shift | `caesar` | `caesar-*.md` |
| IC ~0.066, flat chi² | a `σ` | `subst` | `subst-*.md` |
| IC ~0.038, `L` | a polyalpha | `vigenere` | `vigenere-*.md` |
| English counts, scrambled | a `π` | `railfence`/columnar | `railfence-*.md` |
| reversed ETAOIN | a reflection | `atbash` | `atbash-deep.md` |

## The verify

| Check | Signal | File |
|---|---|---|
| `enc(pt) == ct` | the transform confirmed | `evidence.md` |
| `flag{`/`CTF{` present | the flag | `evidence.md` |
