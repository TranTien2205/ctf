# Channel: SSH/SFTP out

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Encrypted from byte one; only `ip.dst`, timing, and `ssh` record lengths are visible. An SSH session to an external IP during the window IS the finding shape; contents are unreachable without keys. Say 'SSH channel to X carried Y bytes' — never claim content.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
