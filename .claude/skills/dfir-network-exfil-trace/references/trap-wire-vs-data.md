# Trap: frame.len vs payload

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`frame.len` includes all headers; Zeek `orig_bytes` does not; `tcp.len` is payload. Mixing them across one answer silently shifts the number by ~40-66 bytes/packet. Name which produced the figure.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
