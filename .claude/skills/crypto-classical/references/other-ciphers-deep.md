# Other ciphers deep — the named classicals, annotated

## Playfair — the keyed digraph

A 5×5 keyed square (`I`/`J` merged). `pt` in digraphs (an `X` between a
repeated pair):
- **same row** → `c` = the letter to the right.
- **same column** → `c` = the letter below.
- **a rectangle** → `c` = the opposite-corner letter.

`cipher_id` reads a `σ`-ish monoalpha — IC ~0.066 but digraph-structured —
the `ct` letter pairs aren't independent. A script / dcode.fr.

## Affine — `σ(p) = (a·p+b) mod 26`

`gcd(a,26)=1` — 12·26=312 keys — brute-forceable; a linear `σ` — `cipher_id`
reads `subst` (IC~0.066, flat chi²).

## Polybius / Tap — the grid-pairs

A 5×5 (or 6×6) grid; each letter → a (row,col) pair — digits `11`-`55`,
letters `AA`-`EE`, or a tapped pattern. A *fractionation* — pairs not letters.

## Baconian — the A/B encoding

5-bit A/B groups — `ABBA`/`ABABB` — an *encoding* — `enc_detect` may catch
the A/B shape; else a script decodes the 5-bit groups.

## Beaufort / Variant-Beaufort — the Vigenere reciprocals

`c = k - p` / `c = p - k` — `beaufort-autokey*.md`.

## Autokey — `key = primer + pt`

The plaintext supplies the running key — `beaufort-autokey*.md`.

## Gronsfeld — digit-key Vigenere

`key` digits `0-9` — `polyalphabetic-variants*.md`.

## ADFGX / ADFGVX — the WWI field cipher

A 6×6 Polybius + a columnar transposition — `ct` is `ADFGVX` — two stages:
undo the columnar → the Polybius pairs → letters.

## Hill — `c = M p mod 26`

A matrix cipher — `M` from the `n`-blocks — needs a script / Sage.

## The honest status

`classical_solve` covers `caesar`,`vigenere`,`subst`,`atbash`,`railfence`.
The named others need a script / dcode.fr — `cipher_id` reads the family
first.
