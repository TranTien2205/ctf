# Channel: IPv6 paths

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

All filters have `ipv6.*` equivalents (`ipv6.dst`, `tcp.dstport` unchanged). A bundle mixing v4 and v6 needs `-Y 'ip or ipv6'`-style coverage; `endpoints,ipv6` is its own tap. Overlooking v6 silently halves the measured volume.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
