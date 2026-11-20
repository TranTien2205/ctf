# Channel: DNS via TXT/NULL record types

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

`-Y 'dns.qry.type in {10,16}'` — 16 TXT, 10 NULL. These types carry the fattest arbitrary payloads both ways. Distinguish tunnel TXT from SPF/DKIM legit TXT by the label entropy and the parent-domain concentration. `dns,tree` `Query Type` leaf gives the count in one pass.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
