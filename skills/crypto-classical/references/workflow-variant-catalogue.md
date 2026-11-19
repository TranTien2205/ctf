# Workflow variant catalogue — the challenge shapes, indexed

## The shape → the procedure

| Shape | The procedure | The files |
|---|---|---|
| named cipher | `other-ciphers.md` → a script | `workflow-variant*.md` |
| bare blob | `cipher_id` → family → `classical_solve` | `workflow*.md` |
| keyed-but-unnamed | `vigenere`/`subst`, the words first | `workflow-variant*.md` |
| layered | `cipher_id` per layer | `multi-step-chains*.md` |
| encoding | `enc_detect` → `cipher_id` | `encoding-*.md` |
| short blob | `flag{` positions + common letters | `known-plaintext*.md` |
| `n=r·c` blob | `railfence`/columnar/route | `railfence-*.md` |
| `flag{`-visible | the crib → `classical_solve` | `known-plaintext*.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers.md` → a script | `playfair-polybius*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md` — every shape ends here.

## The record

`post-probe` · `classify_solve.py` · `../field-notes.md` · `knowledge/attempts/`.
