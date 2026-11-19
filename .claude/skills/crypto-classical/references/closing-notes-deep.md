# Closing notes deep — crypto-classical, the complete picture

## The class

A classical cipher — a letter-only `ct`, no key material. Five families:
shift, substitution, polyalphabetic, transposition, encoding-boundary. The
violation is the *transform* being weak — statistics reveal it.

## The procedure

`cipher_id.py --text` → `cipher-identification.md` →
`classical_solve.py <family> --text [--keylen|--key|--restarts]` →
`evidence.md` → `../field-notes.md`.

## The statistics → the family

- **IC ~0.066 + one chi² min** → `caesar` — `k` is the min.
- **IC ~0.066, flat chi², ETAOIN shape** → `subst` — a `σ`.
- **IC ~0.038, Kasiski `L`** → `vigenere --keylen L` — `L` Caesars.
- **English counts, scrambled** → `railfence`/columnar — a `π`.
- **Reversed ETAOIN** → `atbash` — the reflection.
- **`+/=`/hex/`01`/`.-`** → `enc_detect` — an encoding, not a cipher.

## The bounds/falsifiers

`k`/`L`/`σ`/depth/`key` — and the closes: no `k`/`L`/language → the family
closes; `+/=`/hex is the enc-vs-cipher discriminator; a layered `ct` —
`cipher_id` on the output.

## The verify

`pt` language + `enc(pt) == ct` + `flag{`/`CTF{` present — the `k`/`L`/`σ`/
depth proven.

## The honest status

**Catalogue** — no local solve. `../field-notes.md` grows with real solves; a
confirm promotes the class.
