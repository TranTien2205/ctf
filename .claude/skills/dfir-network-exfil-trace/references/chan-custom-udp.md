# Channel: Custom UDP protocol

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

`conv,udp` flow with steady `->` bytes, `io,phs` showing `data` under `udp`, no known service. First bytes often fingerprint the tool — `-e data.data | head`. Volume via `udp.length`; content needs the payload carved per `forensics-pcap-carve`.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
