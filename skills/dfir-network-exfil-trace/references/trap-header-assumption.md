# Trap: Hardcoded Zeek columns

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`cut -f13` for `history` lands on `local_orig` in the standard column order — the middle columns moved. Count from the file's own `#fields` line or use `zeek-cut`.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
