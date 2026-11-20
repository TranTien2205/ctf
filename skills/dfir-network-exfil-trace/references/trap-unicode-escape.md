# Trap: \. rejected in display filters

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

tshark 4.0.7 rejects `\.` inside `matches` — use `[.]` instead: `dns.qry.name matches "^[0-9a-f]{16,}[.]"`. Measured error: "\. is not a valid character escape sequence".

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
