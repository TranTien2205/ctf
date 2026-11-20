# Channel: TFTP

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Cleartext, unauthenticated, UDP/69 then ephemeral ports. `--export-objects tftp` IS the file. `skills/ctf-forensics/linux-forensics.md:42-63` has a worked Linux chain ending in TFTP out.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
