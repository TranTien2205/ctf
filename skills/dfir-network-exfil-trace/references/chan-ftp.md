# Channel: FTP exfil

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Unauthenticated-friendly: `-z credentials` often shows USER/PASS cleartext; `ftp.request.command==STOR` marks uploads; `--export-objects ftp-data` recovers the file. Passive-mode data channels live on negotiated ports — the export follows them automatically.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
