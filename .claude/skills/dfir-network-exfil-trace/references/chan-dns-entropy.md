# Channel: Entropy as a DNS tell — and its limit

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Measured on this box at DNS-label length (32-48 chars): prose 3.83, base32 4.37, base64 4.41, HEX 3.72 — entropy does NOT separate hex tunnels from prose. Use entropy only against base32/base64; for hex use the alphabet regex. Command: `python3 -c 'import sys,math,collections;s=sys.argv[1];c=collections.Counter(s);n=len(s);print(round(-sum(v/n*math.log2(v/n) for v in c.values()),2))' <label>`.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
