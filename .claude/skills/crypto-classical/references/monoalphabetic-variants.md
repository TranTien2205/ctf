# Monoalphabetic variants — the `σ` family

## Simple substitution — `c = σ(p)`

Any bijection — the `subst` anneal target. IC~0.066, flat chi², ETAOIN-shaped.

## Keyword — `σ` = `KEYWORD + rest-of-alphabet`

`KEYWORDABCDFGHIJLMNPQRSTUVWXYZ` — the `σ` order reveals the keyword.

## Caesar — `σ` a cyclic shift

`σ(i) = (i+k) mod 26` — a special `σ`; `caesar` (25 `k`) is faster than the
anneal. IC~0.066, chi² one min.

## Atbash — `σ` the reflection

`σ(i) = 25-i` — `atbash --text`; reversed ETAOIN.

## Affine — `σ(p) = (a·p+b) mod 26`

`gcd(a,26)=1` — 12·26=312 keys — brute-forceable; a linear `σ`.

## ROT5/18/47 — the digit/printable shifts

ROT5 digits, ROT18 letters+digits, ROT47 printable ASCII — `codecs`/a script.

## The `π(σ(p))` layered — `σ` first or `π` first

`π` on positions, `σ` on letters — un-scramble `π` (position) then `subst`.

## The `σ`-family detection

IC ~0.066 — all monoalpha preserve the multiset. chi² splits Caesar (one min)
from `subst` (flat); the reversed-ETAOIN names `atbash`.

## The verify

`σ⁻¹(c) = p` language; `σ(p) = c`.
