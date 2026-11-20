# Channel: Legitimate-service abuse

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Paste sites, file-shares, cloud storage, webhook endpoints, git forges, issue trackers, docs platforms. Detection = `http_req,tree` hostnames + volume; the service is legitimate, the CONTENT is the exfil — answer needs the exported body, not the hostname.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
