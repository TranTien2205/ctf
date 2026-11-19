# Summary surface — crypto-classical at a glance, the surface edition

## The class

A classical cipher — letter-only `ct`, no key — shift/subst/polyalpha/
transposition/encoding. `cipher_id` discriminates; `classical_solve` solves.

## The procedure

`cipher_id --text` → `cipher-identification.md` → `classical_solve <f> --text`
→ `evidence.md` → `../field-notes.md`.

## The families → the bounds

| Family | Bound | Command |
|---|---|---|
| `caesar` | `k` in 25 | `classical_solve caesar --text` |
| `atbash` | `c=25-p` | `classical_solve atbash --text` |
| `subst` | a `σ` | `classical_solve subst --text` |
| `vigenere` | `L` + key | `classical_solve vigenere --text [--keylen]` |
| `railfence` | `r`/`w`/`π` | `classical_solve railfence --text` |
| named others | a script | `other-ciphers*.md` |
| encoding | none | `enc_detect` |

## The signals → the families

IC~0.066/0.038/0.05 · chi² `k`/flat/reversed · Kasiski `L` · ETAOIN/flat/
scrambled · charset.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.

## The honest status

**Catalogue** — no local solve.
