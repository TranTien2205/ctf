# Operator checklist catalogue — the field order, indexed

## The setup

- [ ] `cipher_id.py --selftest` / `classical_solve.py <f> --selftest` /
      `enc_detect.py --selftest` — the tools work.
- [ ] the `ct` — letters-only or the charset discriminated —
      `detection.md`,`encoding-*.md`.

## The identify — `cipher_id.py --text 'CT'`

- [ ] the IC — `detection-deep.md`,`frequency-analysis*.md`.
- [ ] the chi² — `detection-deep.md`,`caesar-*.md`.
- [ ] Kasiski — `detection-deep.md`,`vigenere-*.md`,`key-length*.md`.
- [ ] the frequency — `frequency-analysis*.md`.
- [ ] a name/a keyword — `lead-grammar*.md`,`other-ciphers*.md`.
- [ ] `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` positions — `known-plaintext*.md`.
- [ ] the length — `n = r·c` — `railfence-*.md`.

## The route

- [ ] `cipher-identification.md`/`detection-matrix*.md` → the family.
- [ ] `payload-dictionary*.md` → the invocation.
- [ ] `per-family-*.md` → the bound.

## The solve

- [ ] `classical_solve <family> --text [--keylen|--key|--restarts|--iters]`
- [ ] a script / dcode.fr — `other-ciphers*.md`
- [ ] `enc_detect` — `encoding-*.md`

## The verify

- [ ] `pt` language · `enc(pt) == ct` · `flag{`/`CTF{` — `verify*.md`.

## The record

- [ ] `post-probe` · `classify_solve.py` · `../field-notes.md` ·
      `knowledge/attempts/` — `field-notes-catalogue.md`,`negative-*.md`.
