# Trap: SNI treated as destination

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

SNI/Host are client claims. Domain fronting exists to make them lie. `ip.dst` is the observation. A report that says 'exfiltrated to cdn.example' off SNI alone is wrong until `ip.dst` agrees.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
