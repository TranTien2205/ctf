# Channel: Data arriving inside DNS answers

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Tunnels move data both ways: `dns.count.answers` high, `dns.txt`/`dns.resp.name` carrying encoded strings, `dns.data` fields. Questions asking 'what came back' read the RESPONSE side, which `dns.flags.response==0` filters OUT — drop the direction filter for this question.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
