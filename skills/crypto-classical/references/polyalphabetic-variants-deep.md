# Polyalphabetic variants deep — the `L`-coset family, annotated

## Vigenere — `c = p + k_{i mod L}`

The canonical — `L` Caesar shifts cycling. `cipher_id` → IC~0.038, Kasiski
`L` → `vigenere --keylen L` → `L` Caesars.

## Beaufort — `c = k - p` (the reciprocal)

Decrypt = encrypt — `p = k - c`. A Vigenere-decode `p = c - k` gives garbage;
the reciprocal gives `pt`. IC~0.038, Kasiski `L` — the sign is invisible to
the statistics.

## Variant-Beaufort — `c = p - k`

`p = c + k` — a Vigenere with negated key — key `K` decodes a Variant `ct`
with `K' = -K`.

## Autokey — `key = primer + pt`

The running key is the *plaintext* itself — `k_i = pt_{i-1}` — `p_i =
c_i - p_{i-1}` after the primer. **No periodic `L` in Kasiski** — the `pt`
key doesn't repeat — the `L` estimator reads nothing.

## Gronsfeld — a digit-key Vigenere

`key` digits `0-9` — a 10-shift Vigenere — `vigenere --key <digits>`.

## Running-key — a book/long key

`key` a long text — Kasiski fails (no period); a crib or the key text is
needed — `known-plaintext*.md`.

## Keyed-alphabet Vigenere — over `σ`-alphabet

`L` shifts over a `KEYWORD`-mixed alphabet — `vigenere` gives the `L` cosets
+ `k` shifts, then `subst` the per-coset `σ` — `multi-step-chains*.md`.

## The detection — IC~0.038 + Kasiski `L`

- IC ~0.038 — the `L`-mix flattens.
- Kasiski `L` — fixed-key variants only (Vigenere/Beaufort/Variant/Gronsfeld).
- autokey/running-key — no periodic `L` — a crib carries it.

## The solve

`vigenere --text [--keylen|--key]` — `L` cosets → `L` Caesars → the key.

## The falsifier

No `L` produces language → `subst`/`π`/other; or a Beaufort/autokey key shape.
