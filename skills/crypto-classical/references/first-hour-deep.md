# First hour deep — the reads, the output, the budget, annotated

## The reads — `cipher_id.py --text 'CT'`

- **the IC** — ~0.066 mono / ~0.038 poly — the mono/poly split.
- **the chi²** — one min `k` (`caesar`) / flat (`subst`) / reversed (`atbash`).
- **Kasiski** — the `L` (`vigenere --keylen`).
- **the frequency** — ETAOIN-shaped (`σ`) / reversed (`atbash`) / flat
  (polyalpha) / English-counts-scrambled (`π`).
- **the charset** — `+/=`/hex/`01`/`.-` → `enc_detect`, not a cipher.
- **a name in the text** — `other-ciphers.md` for the named others.
- **`flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` positions** — the format leak.
- **the length** — `n = r·c` → a grid → `railfence`/columnar/route.

## The output

A family, a `k`/`L`/`σ`/depth/`key`, and the plaintext — `pt` language →
`enc(pt) == ct` → `flag{`/`CTF{` present → the flag.

## The falsifier-first rule

Read the bound before solving — no `k`/`L`/language → the family closes;
don't re-run. The charset first — `enc_detect` before the cipher statistics.

## The budget

`decide.py` — 5 probes / 15 min per class, 25 / 45 per challenge. `cipher_id`
is one read; `classical_solve` one probe. The 6-rung escalate on a spent
budget — `chain_match`, `reclassify`, `writeup_search`, `novel_plan`,
`fanout_sweep`, `solver_handoff`.

## The record

`post-probe` on a confirm/falsify; `../field-notes.md` after;
`knowledge/attempts/` for a dead end.
