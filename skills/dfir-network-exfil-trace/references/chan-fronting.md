# Channel: Domain fronting

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

TLS SNI says `cdn.example` but `ip.dst` (or inner `http.host` after decryption) disagrees. Quote SNI and ip.dst from the same ClientHello stream. Fronting is a naming lie — the byte counts are unaffected.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
