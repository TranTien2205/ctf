# Workflow playbook — the procedures, indexed

## The discriminate playbook

| Step | The file | The command |
|---|---|---|
| the charset | `detection.md`,`encoding-*.md` | the `+/=`/hex/`01` check |
| `cipher_id` | `detection*.md` | `cipher_id --text` |
| the IC split | `cipher-identification.md` | the mono/poly/`π` read |
| the chi² split | `caesar-*.md`,`subst-*.md`,`atbash-*.md` | the `k`/flat/reversed |
| the Kasiski split | `vigenere-*.md`,`key-length*.md` | the `L` |
| the `n` split | `railfence-*.md` | the `r·c` grid |

## The solve playbook — by family

| Family | The file | The command |
|---|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md` | `classical_solve {caesar,atbash} --text` |
| `subst` | `subst-*.md` | `classical_solve subst --text` |
| `vigenere` | `vigenere-*.md` | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `railfence-*.md` | `classical_solve railfence --text` |
| named others | `other-ciphers.md` | a script / dcode.fr |
| encoding | `encoding-*.md` | `enc_detect` |

## The verify playbook

`verify*.md`,`evidence*.md` — `pt` language + `enc(pt)=ct` + `flag{` present.

## The record playbook

`../field-notes.md` (root),`LEARNING_LOOP`,`knowledge/attempts/`,`post-probe`,
`classify_solve.py`.

## The escalate playbook

`tools/decide.py` — the 6 rungs.
