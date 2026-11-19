# Summary deep — the class, the procedure, the honest status

## The class

A classical cipher — a letter-only `ct`, no key material. Five families:
shift, substitution, polyalphabetic, transposition, encoding-boundary. The
violation is the *transform* being weak — statistics reveal it.

## The procedure

`cipher_id.py --text` → `cipher-identification.md` →
`classical_solve.py <family> --text [--keylen|--key|--restarts]` →
`evidence.md` → `../field-notes.md`.

## The statistics → the family

- IC ~0.066 + one chi² min → `caesar`.
- IC ~0.066, flat chi², ETAOIN shape → `subst`.
- IC ~0.038, Kasiski `L` → `vigenere --keylen`.
- Letters preserved, order scrambled → `railfence`/columnar.
- Reversed alphabet → `atbash`.
- `+/=`/hex/`01`/`.-/` → `enc_detect.py`.

## The bounds/falsifiers

`k`/`L`/`σ`/depth — and the closes: no `k`/`L`/language → family closed;
charset is the enc-vs-cipher discriminator.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.

## The honest status

**Catalogue** — no local solve. `../field-notes.md` grows with real solves.
