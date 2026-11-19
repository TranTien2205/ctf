# Detection checklist surface — the reads, the surface edition

## The charset checklist — the first read

- [ ] `+/=`/hex/`01`/`.-`/`/` → `enc_detect`.
- [ ] `ADFGVX`/`AB`×5 → `other-ciphers`/`playfair-polybius*`.
- [ ] letters-only → `cipher_id`.
- [ ] `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` → the crib.

## The `cipher_id` checklist

- [ ] `cipher_id --text` — the IC/chi²/Kasiski/freq.
- [ ] the IC — mono/poly/`π`.
- [ ] the chi² — `k`/flat/reversed.
- [ ] Kasiski — the `L`.
- [ ] the freq — ETAOIN/reversed/flat/scrambled.

## The context checklist

- [ ] a cipher name — `other-ciphers*.md`.
- [ ] a "key"/"keyword"/"rail"/"fence"/"columns" hint — `lead-grammar*.md`.
- [ ] `flag{`/`CTF{` positions — `known-plaintext*.md`.
- [ ] `n = r·c` — `railfence-*.md`.

## The route checklist

- [ ] `cipher-identification.md` → the family.
- [ ] `payload-dictionary*.md` → the invocation.

## The verify checklist

- [ ] `pt` language · `enc(pt)==ct` · `flag{`/`CTF{` present — `verify*.md`.
