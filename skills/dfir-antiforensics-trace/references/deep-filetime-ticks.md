# Deep: FILETIME precision as evidence

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

100ns ticks since 1601. Real filesystem stamps carry entropy in the low digits; planted stamps built from date strings land on exact seconds (7 trailing zeros). The .0000000 pattern across all four $SI stamps beside nonzero $FN digits is the tell — UNVERIFIED in this tree (no real $MFT parsed); use as support only.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
