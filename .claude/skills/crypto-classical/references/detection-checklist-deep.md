# Detection checklist deep — the reads, ordered, annotated

## Step 0 — the charset

- [ ] letters-only, no spaces → a cipher — the stats apply.
- [ ] `+/=`/hex/`01`/`.-`/`/` → `enc_detect` — *stop*, an encoding.
- [ ] letters+digits → a partial cipher — letters `σ`'d.
- [ ] `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` visible → the format leak.

## Step 1 — `cipher_id --text`

- [ ] the IC — ~0.066 mono / ~0.038 poly / ~0.05-0.066 `π`.
- [ ] the chi² — one min `k` (`caesar`) / flat (`subst`) / reversed (`atbash`).
- [ ] Kasiski — the `L` (`vigenere`).
- [ ] the frequency — ETAOIN (`σ`) / reversed (`atbash`) / flat / scrambled.
- [ ] the verdict — the family.

## Step 2 — the context

- [ ] a cipher name in the text → `other-ciphers.md` if not in the tool.
- [ ] a "key"/"keyword"/"rail"/"fence"/"columns" hint → the family.
- [ ] `flag{`/`CTF{`/`SNT{` positions — the crib.
- [ ] the length — `n = r·c` → a grid.

## Step 3 — the route

- [ ] `cipher-identification.md` → the family.
- [ ] `payload-dictionary.md` → the invocation.

## The falsifier-first rule

The charset *first* — `enc_detect` before the cipher statistics; a `base64`
blob annealed as `subst` is a wasted probe.
