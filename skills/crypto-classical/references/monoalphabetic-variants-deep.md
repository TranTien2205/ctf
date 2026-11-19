# Monoalphabetic variants deep — the `σ` family, annotated

## Simple substitution — `c = σ(p)`, any `σ`

The `subst` anneal target — `classical_solve subst --text`. IC~0.066, flat
chi², ETAOIN-shaped.

## Keyword — `σ = KEYWORD + rest-of-alphabet`

`σ = KEYWORDABCDEFGHIJLMNPQRSTUVWXYZ` — the `σ` order reveals the keyword —
read `σ`'s output sorted by `σ`'s input.

## Caesar — `σ` a cyclic shift

`σ(i) = (i+k) mod 26` — a special `σ` — `caesar` (25 `k`) is faster than the
anneal. IC~0.066, chi² **one min** — the `k` discriminator.

## Atbash — `σ` the reflection

`σ(i) = 25-i` — `atbash --text`; the reversed ETAOIN — `Z`,`V`,`G` top.

## Affine — `σ(p) = (a·p+b) mod 26`

`gcd(a,26)=1` — 12·26=312 keys — brute-forceable; a *linear* `σ` — `cipher_id`
reads it as a `subst` (IC~0.066, flat chi²); a script tries the 312.

## Baconian — a 5-bit A/B *encoding*

`ABBA`/`ABABB`/`ABAB` — an *encoding*, not a `σ` on letters — `enc_detect`
may catch the A/B shape — `playfair-polybius*.md`.

## Polybius — a 5×5 grid pairs

(row,col) → letter — a *fractionation* — the `ct` is pairs — `other-ciphers.md`.

## The `π(σ(p))` layered — `π` first

`π` on positions, `σ` on letters — un-scramble `π` (position) then `subst` —
`multi-step-chains*.md`.

## The `σ`-family detection — IC ~0.066

All monoalpha preserve the multiset. chi² splits Caesar (one min) from `subst`
(flat); the reversed-ETAOIN names `atbash`; digraphs name `playfair`.

## The verify

`σ⁻¹(c) = p` language; `σ(p) = c`.
