# Trap: Retransmissions double-count

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

TCP retransmissions inflate `frame.len`/`conv` bytes; DNS retransmissions inflate query counts and poison chunk reassembly (de-dup before decoding — the working code is in `skills/ctf-forensics/network-advanced.md`). Wire volume vs application data differ by the retransmitted share.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
