# Detection playbook catalogue deep — the discriminate procedures, fully expanded

## The charset playbook — `detection.md`,`encoding-*.md`

`+/=`/hex/`01`/`.-`/`ADFGVX`/`AB`×5 → `enc_detect`/`other-ciphers`. The first
read — an encoding or a fractionation, *stop* before the cipher stats.

## The `cipher_id` playbook — `detection-deep.md`,`detection*.md`

`cipher_id --text` — IC/chi²/Kasiski/freq — the mono/poly/`π` split.

## The family playbook — the per-family procedure

| Family | The procedure | The files |
|---|---|---|
| `caesar`/`atbash` | `classical_solve {caesar,atbash}` — 25/1 | `caesar-*.md`,`atbash-*.md` |
| `subst` | `classical_solve subst [--restarts]` — the anneal | `subst-*.md` |
| `vigenere` | `classical_solve vigenere [--keylen]` — `L` cosets | `vigenere-*.md`,`key-length*.md` |
| `railfence` | `classical_solve railfence` — `r`/`w`/`π` | `railfence-*.md` |
| named others | a script / dcode.fr | `other-ciphers*.md`,`playfair-polybius*.md` |
| encoding | `enc_detect` — no cipher | `encoding-*.md` |

## The route playbook — `cipher-identification.md`

The tuple → the family → `classical_solve`. A wrong family reads as a
no-language `pt` — the falsifier.

## The verify playbook — `verify*.md`,`evidence*.md`

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present — the impact.

## The falsifier playbook — `falsifiers*.md`,`per-falsifier*.md`

The bound before the solve — `caesar`/`atbash` a `pt`-fail *is* the
falsification; `vigenere`/`subst`/`railfence` a tune before.
