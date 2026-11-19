# Detection checklist catalogue — the reads, ordered, indexed

## Step 0 — the charset checklist

- [ ] `+/=`/hex/`01`/`.-`/`/` → `enc_detect` — `encoding-*.md`.
- [ ] `ADFGVX`/`AB`×5 → `other-ciphers`/`playfair-polybius*` — a script.
- [ ] letters-only → a cipher — `cipher-identification.md`.
- [ ] letters+digits → a partial cipher — `edge-cases*.md`.
- [ ] mixed case → a Baconian/binary channel — `edge-cases*.md`.
- [ ] `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` → the crib —
      `known-plaintext*.md`.

## Step 1 — the `cipher_id` checklist

- [ ] `cipher_id --text` — IC/chi²/Kasiski/freq/verdict — `detection*.md`.
- [ ] the IC — ~0.066 mono / ~0.038 poly / ~0.05 `π` —
      `cipher-identification.md`.
- [ ] the chi² — `k`/flat/reversed — `caesar-*.md`,`subst-*.md`,`atbash-*.md`.
- [ ] Kasiski — the `L` — `vigenere-*.md`,`key-length*.md`.
- [ ] the freq — ETAOIN/reversed/flat/scrambled — `frequency-analysis*.md`.
- [ ] the verdict — the family — `per-family-*.md`.

## Step 2 — the context checklist

- [ ] a cipher name — `other-ciphers*.md`.
- [ ] a "key"/"keyword"/"rail"/"fence"/"columns" hint — `lead-grammar*.md`.
- [ ] `flag{`/`CTF{` positions — `known-plaintext*.md`.
- [ ] `n = r·c` — `railfence-*.md`.

## Step 3 — the route checklist

- [ ] `cipher-identification.md` → the family.
- [ ] `payload-dictionary*.md` → the invocation.
- [ ] `per-family-*.md` → the bound.

## The falsifier-first rule

The charset *first* — `enc_detect` before the cipher statistics.
