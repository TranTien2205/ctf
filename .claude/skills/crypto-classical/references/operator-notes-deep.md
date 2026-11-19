# Operator notes deep — the field-guide details, annotated

## The order

`cipher_id` → `cipher-identification` → `classical_solve <family>` →
`evidence` → `field-notes`.

## The tools — the measured interfaces

- `tools/cipher_id.py --text <CT>` / `stdin` / `--selftest` — the identifier.
- `tools/classical_solve.py {caesar,vigenere,subst,atbash,railfence}
  --text <CT> [--keylen L] [--key <word>] [--restarts N] [--iters N]
  [--selftest]` — the solver.
- `tools/enc_detect.py '<CT>` — the encoding path.
- A script / dcode.fr for `other-ciphers.md`'s named others.

## The signals → the families

- IC ~0.066 → monoalpha; ~0.038 → polyalpha.
- chi² min `k` → `caesar`; flat → `subst`; reversed → `atbash`.
- Kasiski `L` → `vigenere --keylen`.
- scrambled letters → `railfence`/columnar.
- `+/=`/hex/`01`/`.-` → `enc_detect`.

## The budget

`decide.py` — 5/15 per class, 25/45 per challenge; the 6-rung escalate.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.

## The record

`post-probe` · `classify_solve.py` · `../field-notes.md` · `knowledge/attempts/`.
