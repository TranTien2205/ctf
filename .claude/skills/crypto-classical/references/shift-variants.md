# Shift variants — the `k`-rotation family

## Caesar — `c = p + k`

25 useful `k`. `classical_solve caesar --text` — the chi² min.

## ROT13 — `k=13`

Self-inverse — `codecs.decode(ct,'rot13')`. `flag{` → `synt{`.

## ROT5 — digits `k=5`

`d → (d+5) mod 10` — the digits only.

## ROT18 — letters ROT13 + digits ROT5

The combined printable shift.

## ROT47 — printable ASCII 33-126 `k=47`

`!..~` rotated by 47 — a `codecs`/`rot47` decode.

## Atbash — `c = 25 - p`

A reflection, not a rotation — `atbash --text`.

## Keyed Caesar — `σ`-alphabet + `k`

`c = keyed[(keyed⁻¹(p) + k) mod 26]` — a shift over a keyed alphabet → the
output is a `σ` — `subst` after the offset.

## The `k`-family detection

IC ~0.066 — a rotation preserves the multiset cyclically. chi² has **one deep
min** at `k` — the un-rotation.

## The verify

`k` → `p = c - k` → language; `c = p + k`.
