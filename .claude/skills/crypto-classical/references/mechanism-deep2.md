# Mechanism deep 2 — the transforms, formalized

## The shift — `c = p + k mod 26`

A cyclic rotation of the alphabet. `k` is the key. Atbash (`c=25-p`) is a
*reflection* — not a rotation — but also a `σ`. The `k`-family is the
chi²-discriminated set; the reflection the reversed-ETAOIN shape.

## The substitution — `c = σ(p)`

A bijection on {A..Z}. The multiset structure is preserved — `σ(E)` is the top
`ct` letter — so the IC is ~0.066 and the frequency *shape* is ETAOIN. The
chi² is flat (no `k` fits a non-rotation). The solve is a tetragram anneal —
the `σ` space is 26! but the anneal climbs locally.

## The polyalphabetic — `c_i = p_i + k_{i mod L}`

`L` cosets each a Caesar. The letters flatten toward uniform — IC ~0.038.
Kasiski: a repeated n-gram at gap `g` → `g` a multiple of `L`. The solve: find
`L` (Kasiski/coset-IC), then `L` Caesars on the cosets.

## The transposition — `c = π(p)`

A permutation of *positions*. The letter multiset is *exactly* preserved —
IC ~0.05-0.066, English counts, scrambled order. The solve: `π`'s shape —
rail-fence (zigzag `r`), columnar (width `w`, key-ordered columns), route
(grid read a path), scytale (fixed-width wrap), block-perm (`b`-blocks).

## The encoding — a structured alphabet, no key

base64 (64-char), hex (16), binary (8×2), Morse (`.-`/`/`), Baconian (A/B×5),
Polybius-pairs — a *bijection of a different kind*: a fixed positional code,
not a `σ` on 26. `enc_detect` decodes.

## The verify

`pt` language + `enc(pt)=ct` — the transform proven.
