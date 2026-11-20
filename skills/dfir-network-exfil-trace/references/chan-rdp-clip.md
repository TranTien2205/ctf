# Channel: RDP/clipboard/file-share

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Interactive channels: RDP drive redirection / clipboard, VNC file transfer, TeamViewer. `rdp`/`vnc` protocol leaves in `io,phs`; the file names ride channel-pdu fields. Rare in CTF bundles but listed for completeness of the channel inventory.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
