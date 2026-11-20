# Channel: SMB write-out

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

`smb2.cmd==9` (WRITE) volume per share/host; `--export-objects smb`. An SMB session to a public IP is itself a finding shape — SMB egress is normally firewall-blocked, so its presence in a capture is noteworthy before content is read.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
