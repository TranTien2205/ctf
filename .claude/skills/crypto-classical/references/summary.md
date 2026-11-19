# Summary — crypto-classical at a glance

## The class

A classical cipher — a letter-only ciphertext, no key — a monoalphabetic,
polyalphabetic, or transposition transform. The attack is the statistics:
IC, chi², Kasiski, frequency.

## The procedure

`cipher_id.py --text` → `cipher-identification.md` →
`classical_solve.py <family> --text` → `evidence.md` → `../field-notes.md`.

## The families

`caesar` (shift, IC~0.066, one chi² min) · `vigenere` (polyalpha, IC~0.038,
Kasiski `L`) · `subst` (bijection, IC~0.066, flat chi²) · `railfence`
(permutation, letters preserved) · `atbash` (reflection) · the named others
(`other-ciphers.md`).

## The bounds

`k`/`L`/`σ`/depth/reflection — and the falsifiers: no `k`/`L`/language closes
the family; `+/=`/hex/`01` is an encoding → `enc_detect.py`.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.

## The honest status

**Catalogue** — no local solve.
