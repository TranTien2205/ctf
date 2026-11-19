# Workflow catalogue deep — the procedures, indexed, annotated

## The read procedures

| Procedure | The file | The output |
|---|---|---|
| `cipher_id` | `detection*.md` | IC/chi²/Kasiski/freq/verdict |
| the charset | `detection.md`,`encoding-vs-cipher.md` | cipher vs encoding |
| the format | `detection.md`,`known-plaintext.md` | `flag{`/`CTF{` positions |
| a name/a keyword | `detection.md`,`lead-grammar.md` | the decoder/family |
| the length/grid | `detection.md`,`railfence-*.md` | a `r·c` shape |

## The discriminate procedure

`cipher-identification.md`,`detection-matrix.md`,`per-family-map.md` —
the (IC × chi² × Kasiski × charset) tuple → the family.

## The solve procedures — by family

| Family | The file | The command |
|---|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`shift-variants.md`,`atbash-*.md` | `classical_solve {caesar,atbash} --text` |
| `subst` | `subst-*.md`,`monoalphabetic-variants.md` | `classical_solve subst --text` |
| `vigenere` | `vigenere-*.md`,`polyalphabetic-variants.md` | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `railfence-*.md`,`transposition-variants.md` | `classical_solve railfence --text` |
| named others | `other-ciphers.md`,`playfair-polybius.md` | a script / dcode.fr |
| encoding | `encoding-vs-cipher.md`,`detection.md` | `enc_detect` |

## The close procedures

| Procedure | The file |
|---|---|
| the verify | `verify.md`,`evidence.md` |
| the record | `../field-notes.md` (root),`LEARNING_LOOP` |
| the escalate | `tools/decide.py` — the 6 rungs |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index.md`,
`summary*.md`,`closing-index.md`.
