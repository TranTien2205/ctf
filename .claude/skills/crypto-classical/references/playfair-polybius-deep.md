# Playfair & Polybius deep — the digraph/grid family, annotated

## Playfair — the keyed digraph cipher

A 5×5 keyed square (`I`/`J` merged). `pt` split into digraphs (an `X` between
a repeated pair); each digraph:
- **same row** → `c` = the letter to the right.
- **same column** → `c` = the letter below.
- **a rectangle** → `c` = the opposite-corner letter.

The `ct` is digraphs — a script / dcode.fr; `cipher_id` reads a `σ`-ish
monoalpha (IC ~0.066, but digraph-structured — the `ct` letter pairs aren't
independent).

## Polybius / Tap — the grid-pairs

A 5×5 (or 6×6 ADFGVX) grid; each letter → a (row,col) pair — digits `11`-`55`,
letters `AA`-`EE`, or a tapped pattern `· ····`/`knock-knock`. A
*fractionation* cipher — the `ct` is pairs, not letters.

## Baconian — the A/B code

5-bit A/B groups — `ABBA`/`ABABB`/... — an *encoding* — `enc_detect` may catch
the A/B shape; else a script decodes the 5-bit groups.

## ADFGX / ADFGVX — the WWI field cipher

A 6×6 Polybius (`A,D,F,G,V,X` labels) + a columnar transposition — `ct` is
`ADFGVX` — two stages: undo the columnar (the `key` orders the columns), then
the Polybius pairs → letters.

## The solve path

`cipher_id` reads a `σ`-ish/`L`-ish family → the *shape* (digraphs, pairs,
A/B, `ADFGVX`) names the variant → `other-ciphers.md` → a script / dcode.fr.

## The verify

`pt` language + the decode reproduced — `flag{` present.
