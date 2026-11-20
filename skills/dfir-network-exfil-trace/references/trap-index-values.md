# Trap: Index values reported as names

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

SRUM `AppId`/`UserId`, WFP `FilterRTID`/`LayerId`, 5156 `Direction` tokens — all are index values into map tables/provider manifests. A raw number reported as the answer is wrong; resolve it first.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
