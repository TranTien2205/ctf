# Glossary deep — every term, expanded

## The statistics

- **IC** (Index of Coincidence) — `Σn_i(n_i-1)/N(N-1)` — the collision
  probability; ~0.066 English, ~0.038 uniform. A `σ`/`π` preserves it; a
  polyalpha mix drops it.
- **chi²** — `Σ(o-e)²/e` — the `k`-shift's fit to English; the min is `k` for
  a Caesar, flat for a `subst`.
- **Kasiski** — the repeated-n-gram `gcd` → `L` — a repeated `pt` n-gram
  encrypted with the same `k` positions.
- **tetragram** — a 4-letter `log p` — the `subst` objective; the anneal
  swaps `σ` entries.
- **frequency** — the letter counts — `ETAOIN` for English.
- **coset** — `ct[j::L]` — the `j`-th `L`-periodic subsequence.
- **crib** — a known `pt` fragment — `flag{`/`CTF{` — anchors `σ`/`k`/`key`.

## The families

- **monoalphabetic** — one `σ` — caesar/subst/atbash/affine.
- **polyalphabetic** — `L` alphabets — vigenere/beaufort/autokey/gronsfeld.
- **transposition** — a `π` — railfence/columnar/route/scytale/block-perm.
- **encoding** — a structured alphabet — base64/hex/binary/morse/baconian —
  no key.
- **fractionation** — a letter → a pair (Polybius/ADFGVX).

## The parameters

- **`k`** — the shift; `L` — the key length; `σ` — the bijection; `π` — the
  permutation; `key` — the word; `a`,`b` — the Affine params; `r`/`w` — the
  rail-fence depth / columnar width.

## The verify

`pt` language + `enc(pt)=ct`.
