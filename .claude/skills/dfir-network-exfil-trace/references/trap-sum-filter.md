# Trap: SUM() silently zero

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`SUM(frame.len)ip.src==X` returns 0 in EVERY interval — the field must appear inside the filter too: `SUM(frame.len)frame.len and ip.src==X`. Measured. An all-zero stat row after this shape is the bug, not the traffic.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
