# Workflow index deep — the phase → the file → the command

| Phase | The file | The command |
|---|---|---|
| read | `detection*.md`,`cipher-identification.md` | `cipher_id --text` |
| discriminate | `cipher-identification.md`,`detection-matrix*.md` | the IC/chi²/Kasiski tuple |
| solve | `payload-dictionary*.md`,`workflow*.md` | `classical_solve <f> --text` |
| verify | `verify.md`,`evidence.md` | `enc(pt)==ct` |
| record | `../field-notes.md` (root),`LEARNING_LOOP` | `post-probe`,`classify_solve` |
| escalate | `tools/decide.py` | the 6 rungs |

## The family procedures

| Family | The file | The command |
|---|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md` | `classical_solve {caesar,atbash} --text` |
| `subst` | `subst-*.md` | `classical_solve subst --text` |
| `vigenere` | `vigenere-*.md` | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `railfence-*.md` | `classical_solve railfence --text` |
| named others | `other-ciphers.md` | a script |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index.md`,
`summary*.md`,`closing-index.md`.
