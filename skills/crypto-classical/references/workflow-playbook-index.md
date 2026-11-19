# Workflow playbook index — the procedures → the files, indexed

## The phase playbooks

| Phase | The playbook files |
|---|---|
| read | `workflow-playbook.md`,`detection*.md` |
| discriminate | `cipher-identification.md`,`detection-matrix*.md` |
| solve | `payload-dictionary*.md`,`workflow-playbook.md`,`workflow*.md` |
| verify | `verify*.md`,`evidence*.md` |
| record | `../field-notes.md`,`field-notes-catalogue.md`,`negative-*.md` |
| escalate | `tools/decide.py`,`falsifiers*.md` |

## The family playbooks

| Family | The playbook files | The command |
|---|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md`,`workflow-playbook.md` | `classical_solve {caesar,atbash}` |
| `subst` | `subst-*.md`,`workflow-playbook.md` | `classical_solve subst` |
| `vigenere` | `vigenere-*.md`,`key-length*.md`,`workflow-playbook.md` | `classical_solve vigenere` |
| `railfence` | `railfence-*.md`,`transposition-variants*.md`,`workflow-playbook.md` | `classical_solve railfence` |
| named others | `other-ciphers*.md`,`playfair-polybius*.md` | a script |
| encoding | `encoding-*.md` | `enc_detect` |

## The shape playbooks

| Shape | The files |
|---|---|
| `enc → cipher → enc` | `multi-step-chains*.md`,`workflow-playbook.md` |
| `π(σ(p))`/`σ(π(p))` | `multi-step-chains*.md`,`railfence-*.md` |
| `flag{`-visible | `known-plaintext*.md`,`workflow-playbook.md` |
| keyed-but-unnamed | `vigenere-*.md`,`subst-*.md` |
| `n = r·c` | `railfence-*.md`,`transposition-variants*.md` |

## The indexes

`README.md`,`workflow-index*.md`,`detection-index*.md`,`map-index*.md`.
