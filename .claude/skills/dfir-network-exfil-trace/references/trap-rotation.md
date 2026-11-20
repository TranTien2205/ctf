# Trap: Rotation read as absence

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

pfirewall.log default cap is 4,096 KB with old entries deleted; journals rotate; captures truncate. Check whether the file starts with its header block or mid-line before calling a missing record absent.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
