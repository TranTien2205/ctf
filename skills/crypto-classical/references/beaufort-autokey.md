# Beaufort & autokey — the Vigenere reciprocals

## Beaufort — `c = k - p`

The *reciprocal* — decrypt is the same operation as encrypt (`p = k - c`). A
Vigenere-decode gives garbage; a Beaufort-decode `p = k - c` gives `pt`.

## Variant-Beaufort — `c = p - k`

The negative — `p = c + k` — a Vigenere with the *negated* key. A Vigenere
with key `K` decodes a Variant-Beaufort `ct` with key `-K`.

## The reciprocal check

`vigenere --key K` gives garbage → try `p = k - c` (Beaufort) or `p = c + k`
(Variant) — the same `L`, a different sign.

## Autokey — `key = primer + pt`

The running key is the *plaintext* itself after a primer. `k_i = pt_i` — the
`ct` is `p + (primer ++ p)`. The decode: `p_0 = c_0 - primer`, then `p_i =
c_i - p_{i-1}` — each `pt` letter supplies the next key.

## Gronsfeld — a digit-key Vigenere

`key` digits 0-9 — the `vigenere` path with a numeric `key`.

## The detection

IC ~0.038 (polyalpha); Kasiski `L` (fixed-key variants) — autokey has no
periodic `L` (the `pt` key doesn't repeat).

## The verify

`p = c - k_{i mod L}` (Vigenere), `p = k - c` (Beaufort), `p = c_i - p_{i-1}`
(autokey) — language out.
