# Channel: Local-segment ambiguity

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Inside one L2 segment, `eth.dst` resolves which local device packets left toward; for a routed peer, `eth.dst` is just the gateway MAC. Don't report the gateway MAC as the exfil peer — `ip.dst` is the answer.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
