# Trap: S0/REJ counted as transfer

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Failed dials (conn_state S0/REJ) carry no payload — including their flows in 'what left' overstates the exfil. Filter `conn_state==SF` (or check pcap for established flows) before summing.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
