# Deep: TXT record payload shape

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

TXT carries <character-string> fields up to 255 bytes each, multiple per record. `dns.txt` surfaces them; inbound smuggling via TXT is visible without decoding the whole record. NULL records (type 10) carry arbitrary bytes with no string framing.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
