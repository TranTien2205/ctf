# Checklist — the solve, step by step

## The reads

- [ ] `cipher_id.py --text` — IC/chi²/Kasiski/freq/verdict
- [ ] the charset — letters-only vs `+/=`/hex/`01`/`.-`
- [ ] a name in the text — the decoder
- [ ] `flag{`/`CTF{`/`SNT{` positions
- [ ] the length — a grid/route shape

## The discriminate

- [ ] `cipher-identification.md` — the tuple → the family

## The solve

- [ ] `classical_solve <family> --text [--keylen|--key|--restarts]`

## The verify

- [ ] `pt` language
- [ ] `enc(pt) == ct`
- [ ] `flag{`/`CTF{` present

## The record

- [ ] `post-probe --hypothesis-id --class crypto-classical --verdict ...`
- [ ] `classify_solve.py --chain <id>`
- [ ] `../field-notes.md`

## The escalate

- [ ] `decide.py` — the 6 rungs on a spent budget
