# Glossary — every term

## The statistics

- **IC** (Index of Coincidence) — `Σn_i(n_i-1)/N(N-1)` — the collision
  probability; ~0.066 English, ~0.038 random.
- **chi²** — `Σ(o-e)²/e` — the frequency fit per shift; the min is `k`.
- **Kasiski** — the repeated-n-gram gcd → `L`.
- **tetragram** — a 4-letter sequence's `log p` — the `subst` objective.
- **frequency** — the letter counts; ETAOIN-shaped.

## The families

- **monoalphabetic** — one `σ` — caesar/subst/atbash/affine.
- **polyalphabetic** — `L` alphabets — vigenere/beaufort/autokey/gronsfeld.
- **transposition** — a `π` — railfence/columnar/route/scytale.
- **encoding** — a structured alphabet, no key — base64/hex/binary/morse/
  baconian.

## The parameters

- **`k`** — the shift; `L` — the key length; `σ` — the bijection; `π` — the
  permutation; `key` — the word.

## The verify

`pt` language + `enc(pt)=ct`.
