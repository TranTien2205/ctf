# Channel: Timing/covert-channel encoding

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Data encoded in inter-packet gaps rather than payload. Detection is the beacon arithmetic run on a flow with TINY payloads: uniform deltas with two distinct levels = binary encoding. Worked interval-to-bit code: `skills/ctf-forensics/network-advanced.md:26-63`.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
