# Detection checklist map — the reads → the family → the file

## The charset checklist → the file

| Read | The files |
|---|---|
| `+/=`/hex/`01`/`.-`/`/` | `encoding-*.md`,`detection.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers*.md`,`playfair-polybius*.md` |
| letters-only | `cipher-identification.md` |
| letters+digits | `edge-cases*.md` |
| mixed case | `edge-cases*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | `known-plaintext*.md` |
| `n = r·c` | `railfence-*.md`,`transposition-variants*.md` |
| a name/a keyword | `other-ciphers*.md`,`lead-grammar*.md` |

## The `cipher_id` checklist → the file

| Read | The files |
|---|---|
| IC ~0.066 | `cipher-identification.md`,`caesar-*.md`,`subst-*.md`,`atbash-*.md` |
| IC ~0.038 | `vigenere-*.md` |
| IC ~0.05 | `railfence-*.md` |
| chi² `k` | `caesar-*.md` |
| chi² flat | `subst-*.md` |
| reversed | `atbash-*.md` |
| Kasiski `L` | `vigenere-*.md`,`key-length*.md` |
| ETAOIN | `subst-*.md`,`frequency-analysis*.md` |
| scrambled | `railfence-*.md` |
| digraphs | `playfair-polybius*.md` |

## The route files

`cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md`,
`workflow*.md`,`payload-dictionary*.md`.
