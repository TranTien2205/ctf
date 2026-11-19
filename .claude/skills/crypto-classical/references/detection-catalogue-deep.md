# Detection catalogue deep — the reads, fully indexed, annotated

## The tool reads — the measured interfaces

| Read | Output | The files |
|---|---|---|
| `cipher_id --text 'CT'` | IC/chi²/Kasiski/freq/verdict | `detection*.md`,`cipher-identification.md` |
| `cipher_id --selftest` | the offline self-test | `preconditions.md` |
| `enc_detect 'CT'` | the encoding path | `encoding-*.md` |
| `classical_solve <f> --selftest` | the solver works | `preconditions.md` |

## The observable reads — the `ct` shape

| Observable | The read | The files |
|---|---|---|
| the charset | cipher vs encoding | `detection.md`,`detection-checklist*.md`,`detection-surface*.md` |
| the IC | ~0.066/0.038/0.05 | `detection-deep.md`,`theory*.md`,`frequency-analysis*.md` |
| the chi² | `k`/flat/reversed | `detection-deep.md`,`caesar-*.md`,`subst-*.md`,`atbash-*.md` |
| Kasiski | the `L` | `detection-deep.md`,`vigenere-*.md`,`key-length*.md` |
| the frequency | ETAOIN/reversed/flat/scrambled | `frequency-analysis*.md`,`subst-*.md`,`atbash-*.md` |
| the digraphs | `σ`-preserved/`π`-broken | `frequency-analysis*.md`,`playfair-polybius*.md` |
| the format | `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` | `known-plaintext*.md`,`case-studies*.md` |
| a name/a keyword | the decoder/family | `lead-grammar*.md`,`other-ciphers.md` |
| the length/grid | `n = r·c` | `railfence-*.md`,`transposition-variants*.md` |

## The route reads — the family → the file

| Read | The files |
|---|---|
| the family | `cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md` |
| the invocation | `payload-dictionary*.md`,`workflow-map.md`,`workflow-playbook.md` |
| the falsifier | `falsifiers*.md`,`per-falsifier*.md`,`falsifier-map.md` |
| the verify | `verify*.md`,`evidence*.md` |
| the record | `field-notes-catalogue.md`,`negative-*.md` |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`,
`summary*.md`,`closing-index.md`.
