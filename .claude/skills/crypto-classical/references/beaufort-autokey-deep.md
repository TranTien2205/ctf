# Beaufort & autokey deep — the Vigenere reciprocals, annotated

## Beaufort — `c = k - p` (the reciprocal)

The *reciprocal* cipher — decrypt is the same operation as encrypt:
`p = k - c`. A Vigenere-decode `p = c - k` gives garbage; a Beaufort-decode
`p = k - c` gives `pt`. The `k` positions cycle like Vigenere — `L` is the
key length.

## Variant-Beaufort — `c = p - k`

`p = c + k` — a Vigenere with the *negated* key. A Vigenere with key `K`
decodes a Variant-Beaufort `ct` with key `K'` where `K'[j] = -K[j]`.

## The reciprocal check — when `vigenere` fails

`vigenere --key K` gives garbage → try `p = k - c` (Beaufort) or `p = c + k`
(Variant) — the same `L`, a different sign. `cipher_id` still reads IC~0.038
and Kasiski `L` — the sign is invisible to the statistics.

## Autokey — `key = primer + pt`

The running key is the *plaintext* itself after a primer. `k_i = pt_{i-1}` —
the `ct` is `p + (primer ++ p)`. The decode: `p_0 = c_0 - primer`, then
`p_i = c_i - p_{i-1}` — each `pt` letter supplies the next key. No periodic
`L` in Kasiski — the `pt` key doesn't repeat.

## Gronsfeld — a digit-key Vigenere

`key` digits `0-9` — a 10-shift Vigenere — `vigenere --key <digits>`.

## Running-key — a book/long key

`key` a long text (a book, a poem) — Kasiski fails (no period); a crib or the
key text is needed.

## The detection

IC ~0.038 (polyalpha); Kasiski `L` (fixed-key variants) — autokey/running-key
have no periodic `L`.

## The verify

`p = c - k_{i mod L}` (Vigenere), `p = k - c` (Beaufort), `p = c_i - p_{i-1}`
(autokey) — language out.
