# Mechanism — the five families, compact

## Shift (Caesar / ROT / Atbash)

`c = p + k mod 26` — a cyclic shift. Atbash is `c = 25 - p` (a reflection). A
monoalphabetic — `σ` a rotation; the ETAOIN spikes shift by `k`. The chi² min
finds `k`.

## Substitution

`c = σ(p)` — a bijection. The frequency *shape* survives — `σ(E)` is the
common `ct` letter. IC ~0.066. The annealing climbs the tetragram score by
swapping `σ` entries.

## Polyalphabetic (Vigenere)

`c_i = p_i + k_{i mod L}` — `L` cosets each a Caesar. The mix flattens — IC
~0.038. Kasiski: a repeated n-gram at gap `g` → `g` a multiple of `L`.

## Transposition

`c = π(p)` — a permutation of *positions*. The letter counts are unchanged —
the IC is near-English but the order is scrambled. Rail-fence/columnar/route
differ in `π`'s shape.

## Encoding (the boundary)

A structured alphabet — base64 (64-char), hex (16), binary (8×2), Morse
(`.-`), Baconian (A/B×5) — no key. `enc_detect.py` decodes directly. The
charset is the tell.

## The verify

`pt` language + `enc(pt) = ct`.
