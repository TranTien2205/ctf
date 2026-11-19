# Workflow surface — the procedures, the surface edition

## The reads surface

`cipher_id --text` — IC/chi²/Kasiski/freq/verdict — `detection*.md`.

## The route surface

`cipher-identification.md` — the tuple → the family — `per-family-*.md`.

## The solve surface — the commands

| Family | The command |
|---|---|
| `caesar` | `classical_solve caesar --text` |
| `atbash` | `classical_solve atbash --text` |
| `subst` | `classical_solve subst --text` |
| `vigenere` | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `classical_solve railfence --text` |
| named others | `other-ciphers.md` → a script |
| encoding | `enc_detect` |

## The verify surface

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present — `verify*.md`.

## The record surface

`post-probe` · `classify_solve.py` · `../field-notes.md` · `knowledge/attempts/`.

## The escalate surface

`decide.py` — the 6 rungs.
