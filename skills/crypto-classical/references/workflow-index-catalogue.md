# Workflow index catalogue — the procedures, fully indexed

## The phase procedures

| Phase | The files | The command |
|---|---|---|
| read | `detection*.md`,`cipher-identification.md` | `cipher_id --text` |
| discriminate | `cipher-identification.md`,`detection-matrix*.md` | the tuple → family |
| solve | `payload-dictionary*.md`,`workflow*.md` | `classical_solve <f> --text` |
| verify | `verify*.md`,`evidence*.md` | `enc(pt)==ct` |
| record | `../field-notes.md`,`negative-*.md` | `post-probe`,`classify_solve` |
| escalate | `tools/decide.py` | the 6 rungs |

## The family procedures — the files → the commands

| Family | The files | The command |
|---|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md`,`shift-variants*.md` | `classical_solve {caesar,atbash} --text` |
| `subst` | `subst-*.md`,`monoalphabetic-variants*.md`,`language-scoring*.md` | `classical_solve subst --text [--restarts]` |
| `vigenere` | `vigenere-*.md`,`polyalphabetic-variants*.md`,`beaufort-autokey*.md`,`key-length*.md` | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `railfence-*.md`,`transposition-variants*.md` | `classical_solve railfence --text` |
| named others | `other-ciphers*.md`,`playfair-polybius*.md` | a script / dcode.fr |
| encoding | `encoding-*.md`,`detection.md` | `enc_detect` |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`,
`summary*.md`,`closing-index.md`.
