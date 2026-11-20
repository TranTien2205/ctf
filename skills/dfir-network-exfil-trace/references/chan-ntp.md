# Channel: NTP/UDP-123 carry

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

NTP-shaped flow to an odd port or with fat client fields. `ntp.*` fields exist; a 'NTP' flow with 200-byte requests to one peer is shape-wrong. Rare but cheap to check with `udp.dstport==123` + length histogram.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
