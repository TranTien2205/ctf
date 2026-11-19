# Checklist deep — the solve, step by step, annotated

## The reads — `cipher_id.py --text 'CT'`

- [ ] the charset — letters-only vs `+/=`/hex/`01`/`.-`/`ADFGVX`
- [ ] the IC — ~0.066 mono / ~0.038 poly / ~0.05 `π`
- [ ] the chi² — one min `k` (`caesar`) / flat (`subst`) / reversed (`atbash`)
- [ ] Kasiski — the `L` (`vigenere`)
- [ ] the frequency — ETAOIN (`σ`) / reversed (`atbash`) / flat / scrambled (`π`)
- [ ] a cipher name in the text — `other-ciphers.md` if not in the tool
- [ ] a "key"/"keyword"/"rail"/"fence"/"columns" hint
- [ ] `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` positions — the crib
- [ ] the length — `n = r·c` → a grid → `railfence`/columnar/route

## The discriminate

- [ ] `cipher-identification.md` / `detection-matrix.md` — the tuple → family
- [ ] `per-family-map.md` — the family → the bound → the file

## The solve

- [ ] `classical_solve <family> --text [--keylen|--key|--restarts|--iters]`
- [ ] a script / dcode.fr for `other-ciphers.md`'s named others
- [ ] `enc_detect` if the charset says encoding

## The verify

- [ ] `pt` language
- [ ] `enc(pt) == ct`
- [ ] `flag{`/`CTF{` present

## The record

- [ ] `post-probe --hypothesis-id --class crypto-classical --verdict ...`
- [ ] `classify_solve.py --chain <id>`
- [ ] `../field-notes.md` / `knowledge/attempts/`

## The escalate

- [ ] `decide.py` — the 6 rungs on a spent budget
