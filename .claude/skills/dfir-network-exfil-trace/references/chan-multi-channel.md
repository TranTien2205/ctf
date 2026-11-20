# Channel: Split across channels

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

A question like 'how did the file leave' can have a multi-part answer: DNS for signalling, HTTPS for bulk, ICMP for liveness. `io,phs` percentages + per-protocol volume per peer separates the channels. Report each channel's measured share — do not guess the split.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
