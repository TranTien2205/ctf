# Operator checklist deep — the field order, annotated

## The setup

- [ ] `cipher_id.py --selftest` — the tool works.
- [ ] `classical_solve.py <family> --selftest` — the solver works.
- [ ] the `ct` — letters-only or the charset discriminated.

## The identify

- [ ] `cipher_id.py --text` — the IC/chi²/Kasiski/freq.
- [ ] the charset — `+/=`/hex/`01`/`.-` → `enc_detect`.
- [ ] a name in the text — `other-ciphers.md` if not in the tool.
- [ ] `flag{`/`CTF{`/`SNT{` positions — the crib.
- [ ] the length — `n = r·c` → a grid.

## The route

- [ ] `cipher-identification.md` → the family.
- [ ] `payload-dictionary.md` → the invocation.
- [ ] `per-family-map.md` → the bound.

## The solve

- [ ] `classical_solve <family> --text [--keylen|--key|--restarts|--iters]`
- [ ] a script / dcode.fr for `other-ciphers.md`.
- [ ] `enc_detect` if the charset says encoding.

## The verify

- [ ] `pt` language · `enc(pt) == ct` · `flag{`/`CTF{` present.

## The record

- [ ] `post-probe` · `classify_solve.py` · `../field-notes.md` ·
      `knowledge/attempts/` · `decide.py` budget.
