# Operator checklist — the field order

## The setup

- [ ] `cipher_id.py --selftest` — the tool works.
- [ ] `classical_solve.py <family> --selftest` — the solver works.
- [ ] the `ct` — letters-only or the charset discriminated.

## The identify

- [ ] `cipher_id.py --text` — the IC/chi²/Kasiski/freq.
- [ ] the charset — cipher vs encoding.
- [ ] a name in the text — `other-ciphers.md` if not in the tool.
- [ ] `flag{`/`CTF{`/`SNT{` positions.

## The route

- [ ] `cipher-identification.md` → the family.
- [ ] `payload-dictionary.md` → the invocation.

## The solve

- [ ] `classical_solve <family> --text [--keylen|--key|--restarts]`
- [ ] a script / dcode.fr for the named others.

## The verify

- [ ] `pt` language · `enc(pt) == ct` · `flag{`/`CTF{` present.

## The record

- [ ] `post-probe` · `classify_solve.py` · `../field-notes.md` · `decide.py` budget.
