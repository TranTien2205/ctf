# Channel: Baseline differencing

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

If the bundle ships a clean capture next to the suspect one, diff the per-peer volumes: `comm`/`join` over `endpoints,ip` rows of the two files. Peers only in the suspect capture are the candidate set — much stronger than ranking in one capture.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
