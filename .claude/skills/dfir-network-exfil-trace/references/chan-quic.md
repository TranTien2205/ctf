# Channel: QUIC (UDP/443)

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

HTTP/3 rides QUIC over UDP — `udp.dstport==443` flows are NOT DNS and not 'weird UDP'; they are QUIC. SNI-equivalent lives in the QUIC Initial ClientHello (`quic` dissector handles it where built). Misreading QUIC as a UDP tunnel is a classic false positive.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
