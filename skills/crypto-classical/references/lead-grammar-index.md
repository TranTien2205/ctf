# Lead grammar index — the description cues → the files

## The cipher-name cues

| Cue | The cipher | The files |
|---|---|---|
| "caesar"/"shift"/"rot"/"N" | `caesar` | `caesar-*.md`,`lead-grammar*.md` |
| "atbash"/"reverse" | `atbash` | `atbash-*.md` |
| "vigenere"/"key"/"polyalphabetic" | `vigenere` | `vigenere-*.md` |
| "beaufort"/"autokey" | `beaufort-autokey` | `beaufort-autokey*.md` |
| "substitution"/"cipher" | `subst` | `subst-*.md` |
| "rail"/"fence"/"zigzag" | `railfence` | `railfence-*.md` |
| "column"/"transposition" | `columnar` | `transposition-variants*.md` |
| "playfair"/"digraph" | `playfair` | `playfair-polybius*.md` |
| "polybius"/"square"/"tap" | `polybius` | `playfair-polybius*.md` |
| "adfgvx"/"fraction" | `adfgvx` | `other-ciphers*.md` |
| "hill"/"matrix" | `hill` | `other-ciphers*.md` |
| "affine" | `affine` | `monoalphabetic-variants*.md` |
| "scytale" | `scytale` | `transposition-variants*.md` |
| "bacon"/"AB"×5 | `baconian` | `other-ciphers*.md` |
| "morse"/".-" | `morse` | `encoding-*.md` |
| "base64"/"hex"/"binary" | `enc` | `encoding-*.md` |

## The parameter cues

| Cue | The parameter | The files |
|---|---|---|
| "key"/"keyword" | `vigenere`/`subst` key | `vigenere-*.md`,`subst-*.md` |
| "shift"/"rot N" | `caesar` `k` | `caesar-*.md` |
| "rails"/"depth" | `railfence` `r` | `railfence-*.md` |
| "columns"/"width" | `columnar` `w` | `transposition-variants*.md` |
| "period"/"length" | `vigenere` `L` | `vigenere-*.md`,`key-length*.md` |
| "a,b" | `affine` | `monoalphabetic-variants*.md` |

## The shape cues

| Cue | The shape | The files |
|---|---|---|
| `synt{`/`Pxl{`/`fhpnf{` | `caesar` | `caesar-*.md`,`known-plaintext*.md` |
| `gLAG{` | `subst` near-decode | `subst-*.md` |
| `ADFGVX`-alphabet | `adfgvx` | `other-ciphers*.md` |
| `n = r·c` | a grid `π` | `railfence-*.md` |
| mixed case | a channel | `edge-cases*.md` |

## The files

`lead-grammar*.md`,`cipher-identification.md`,`detection*.md`.
