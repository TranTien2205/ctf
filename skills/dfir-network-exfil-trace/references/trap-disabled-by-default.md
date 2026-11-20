# Trap: Absent telemetry read as innocence

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Sysmon 3 is disabled by default; 5156 needs its audit subcategory; pfirewall.log logs nothing until enabled; SRUM is silent on hosts where the service never ran. Each absence is a CONFIGURATION fact — say 'not logged', never 'did not happen'.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
