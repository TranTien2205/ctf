# Polyalphabetic variants — the `L`-coset family

## Vigenere — `c = p + k_{i mod L}`

The canonical — `L` Caesar shifts cycling. `cipher_id` → IC~0.038, Kasiski
`L` → `vigenere --keylen L` → `L` Caesars.

## Beaufort — `c = k - p` (reciprocal)

Decrypt = encrypt. Try `p = k - c`.

## Variant-Beaufort — `c = p - k`

`p = c + k` — Vigenere with negated key.

## Autokey — `key = primer + pt`

The plaintext supplies the running key — no periodic `L` in Kasiski; `p_i =
c_i - p_{i-1}` after the primer.

## Gronsfeld — digit-key Vigenere

`key` digits 0-9 — a 10-shift Vigenere.

## Running-key — a book/long key

`key` a long text — Kasiski fails; a crib / the key text needed.

## Keyed-alphabet Vigenere — over `σ`-alphabet

`L` shifts over a `KEYWORD`-mixed alphabet — `vigenere` gives the `L` cosets,
then `subst` the per-coset alphabet.

## The detection

IC ~0.038 + Kasiski `L` (fixed-key) — autokey/running-key have no periodic `L`.

## The verify

`p_i = c_i - k_{i mod L}` → language.
