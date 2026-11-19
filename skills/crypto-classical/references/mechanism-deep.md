# Mechanism deep — the five families, annotated

## Shift (Caesar / ROT / Atbash)

`c = p + k mod 26` — a cyclic shift `k`. Atbash is `c = 25 - p` (reflection).
A monoalphabetic — σ is a rotation; the ETAOIN spikes shift by `k`. The
chi-squared finds `k` — the minimum.

## Substitution

`c = σ(p)` — any bijection. The frequency *shape* (which letters are common)
survives — σ(E) is the common `ct` letter. IC ~0.066 — a bijection preserves
the multiset structure. The annealing climbs the tetragram score by swapping
σ entries.

## Polyalphabetic (Vigenere)

`c_i = p_i + k_{i mod L}` — `L` cosets each a Caesar. The letters flatten —
each position's distribution is a mix of `L` shifts → IC ~0.038. Kasiski: a
repeated n-gram at gap `g` → `g` a multiple of `L`.

## Transposition

`c = π(p)` — a permutation of positions. The *letter counts* are unchanged —
the IC is near-language but the *order* is scrambled. Rail-fence/columnar/
route differ in `π`'s shape.

## Encoding (the boundary)

A structured alphabet — base64 (64-char), hex (16-char), binary (2×8), Morse
(`.- /`), Baconian (A/B×5) — no key. `enc_detect.py` decodes it directly.
The charset is the tell — not a classical cipher.

## The verify

`pow`-equivalent: `pt` is language + `enc(pt)` = `ct`.
