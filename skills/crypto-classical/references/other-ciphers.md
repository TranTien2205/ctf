# Other ciphers — the named classicals not in `classical_solve`

## Playfair

A 5×5 keyed square, digraphs. `c` digraphs in the same row/col/rectangle →
shifted/replaced. Digraphs in the `ct`; no solver here — dcode.fr or a script.

## Affine

`σ(p) = (a·p + b) mod 26`, `gcd(a,26)=1` — 12·26 = 312 keys, brute-forceable.

## Polybius / Tap

A 5×5 grid; pairs of digits/letters → a letter. `ct` of digit-pairs or a
tapping pattern.

## Baconian

5-bit A/B groups — `ABBA AAAAA ...` — an *encoding* not a `σ`. `enc_detect`
may catch it.

## Beaufort / Variant-Beaufort

`c = k - p` / `c = p - k` — the `vigenere` family reciprocal — try the
reciprocal decode.

## Autokey

`key = primer + pt` — the plaintext supplies the running key; decode with the
primer.

## Gronsfeld

Vigenere with digit key `0-9` — the `vigenere` path with a numeric key.

## ADFGX / ADFGVX

A 6×6 Polybius + columnar — `A,D,F,G,V,X` ciphertext — two-stage.

## Hill

`c = M p mod 26` — a matrix — `M` from the `n`-blocks (needs a script).

## The honest status

`classical_solve` covers `caesar`,`vigenere`,`subst`,`atbash`,`railfence`.
The named others need a script / dcode.fr — the `cipher_id` IC/Kasiski/freq
still discriminates the *family* first.
