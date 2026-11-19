# Workflow variant catalogue deep — the shapes → the procedures, indexed

## The shape → the procedure → the files

| Shape | The procedure | The files |
|---|---|---|
| named cipher | `other-ciphers*.md` → a script | `workflow-variant*.md`,`other-ciphers*.md` |
| bare blob | `cipher_id` → family → `classical_solve` | `workflow*.md` |
| keyed-but-unnamed | `vigenere`/`subst`, the words first | `workflow-variant*.md`,`vigenere-*.md` |
| layered `enc → cipher → enc` | `cipher_id` per layer | `multi-step-chains*.md` |
| encoding | `enc_detect` → `cipher_id` | `encoding-*.md` |
| short blob | `flag{` positions + common letters | `known-plaintext*.md`,`edge-cases*.md` |
| `n=r·c` blob | `railfence`/columnar/route | `railfence-*.md`,`transposition-variants*.md` |
| `flag{`-visible | the crib → `classical_solve` | `known-plaintext*.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers*.md` → a script | `playfair-polybius*.md` |
| `π(σ(p))` layered | `π` first, then `subst` | `railfence-*.md`,`multi-step-chains*.md` |
| `σ(π(p))` layered | `σ` first, then `π` | `multi-step-chains*.md` |
| keyed-alphabet Vigenere | `vigenere` `L`, then `subst` | `vigenere-*.md`,`multi-step-chains*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md` — every shape ends here.

## The record

`post-probe` · `classify_solve.py` · `../field-notes.md` · `knowledge/attempts/`
— `field-notes-catalogue.md`,`negative-*.md`.
