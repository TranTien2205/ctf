# Workflow catalogue variant — the procedures, by phase

## The read procedures — `detection*.md`

| Procedure | The file | The output |
|---|---|---|
| `cipher_id` | `detection*.md` | IC/chi²/Kasiski/freq/verdict |
| `enc_detect` | `encoding-*.md` | an encoding |
| the charset | `detection.md` | cipher vs encoding |
| the format | `known-plaintext*.md` | the crib |
| a name/a keyword | `lead-grammar*.md`,`other-ciphers*.md` | the decoder/family |
| the `n` grid | `railfence-*.md` | `r·c` |

## The discriminate procedures — `cipher-identification.md`

`cipher-identification.md`,`detection-matrix*.md`,`per-family-*.md` —
the (IC × chi² × Kasiski × charset) tuple → the family.

## The solve procedures — `payload-dictionary*.md`

| Family | The file | The command |
|---|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md` | `classical_solve {caesar,atbash} --text` |
| `subst` | `subst-*.md` | `classical_solve subst --text [--restarts]` |
| `vigenere` | `vigenere-*.md` | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `railfence-*.md` | `classical_solve railfence --text` |
| named others | `other-ciphers*.md` | a script |
| encoding | `encoding-*.md` | `enc_detect` |

## The close procedures — `verify*.md`,`evidence*.md`,`negative-*.md`

`verify*.md` (`enc(pt)==ct`), `evidence*.md` (the standard),
`../field-notes.md`/`LEARNING_LOOP`/`knowledge/attempts/` (the record),
`decide.py` (the escalate).

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`map-index*.md`.
