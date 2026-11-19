# Detection checklist — the reads, ordered

- [ ] the charset — letters-only vs `+/=`/hex/`01`/`.-`/digits
- [ ] `cipher_id.py --text` — the IC/chi²/Kasiski/frequency
- [ ] a name in the challenge text — `caesar`/`vigenere`/`playfair`/etc
- [ ] a "key"/"keyword"/"rail"/"fence" hint
- [ ] `flag{`/`CTF{` at a position — the format leak
- [ ] the length — a grid/route shape
- [ ] the IC — ~0.066 monoalpha / ~0.038 polyalpha
- [ ] the chi² — one min `k` / flat
- [ ] Kasiski — an `L`
- [ ] the verdict — the family

## The falsifier-first rule

The charset first — `enc_detect` before the cipher statistics.
