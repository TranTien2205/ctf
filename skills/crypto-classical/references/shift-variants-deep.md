# Shift variants deep — the `k`-rotation family, annotated

## Caesar — `c = p + k`, `k` arbitrary

`classical_solve caesar --text` — the 25 `k` ranked by chi²; the min is `k`.

## ROT13 — `k=13`, self-inverse

`codecs.decode(ct, 'rot13')` — `flag{` → `synt{`. A flag that reads `synt{...}`
is the ROT13 of the flag — decode it.

## ROT5 — digits `k=5`

`d → (d+5) mod 10` — digits only — a `rot5` script / CyberChef.

## ROT18 — letters ROT13 + digits ROT5

The combined printable shift — letters `k=13`, digits `k=5`.

## ROT47 — printable ASCII 33-126 `k=47`

`!..~` rotated by 47 — `codecs`/`rot47` — the charset is `!..~` not `A-Z`.

## Atbash — `c = 25 - p`

A *reflection*, not a rotation — `atbash --text`; reversed ETAOIN.

## Keyed Caesar — `σ`-alphabet + `k`

`c = keyed[(keyed⁻¹(p) + k) mod 26]` — a shift over a `KEYWORD`-mixed
alphabet → the output is a `σ` — `subst` on the output — the `k` offset is
absorbed into the `σ`.

## The `k`-family detection — the chi²

IC ~0.066 — a rotation preserves the multiset cyclically. chi² has **one deep
min** at `k` — the un-rotation. A `subst` is flat — no `k` fits a non-
rotation.

## The verify

`k` → `p = c - k` → language; `c = p + k`.

## The traps

- **`k=13` on `pt`** — `flag{` reads `synt{` — decode it.
- **A keyed alphabet** — `subst` on the `k`-shifted output.
- **ROT5/18/47** — a `codecs`/`rot` script, not `caesar --text`.
