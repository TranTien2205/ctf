# Workflow index surface — the procedures, the surface edition

## The phases → the files → the commands

| Phase | The files | The command |
|---|---|---|
| read | `detection*.md` | `cipher_id --text` |
| discriminate | `cipher-identification.md`,`detection-matrix*.md` | the tuple → family |
| solve | `payload-dictionary*.md`,`workflow*.md` | `classical_solve <f> --text` |
| verify | `verify*.md`,`evidence*.md` | `enc(pt)==ct` |
| record | `../field-notes.md`,`negative-*.md` | `post-probe`,`classify_solve` |
| escalate | `tools/decide.py` | the 6 rungs |

## The family → the file → the command

| Family | The file | The command |
|---|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md` | `classical_solve {caesar,atbash} --text` |
| `subst` | `subst-*.md` | `classical_solve subst --text` |
| `vigenere` | `vigenere-*.md` | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `railfence-*.md` | `classical_solve railfence --text` |
| named others | `other-ciphers*.md` | a script |
| encoding | `encoding-*.md` | `enc_detect` |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`.
