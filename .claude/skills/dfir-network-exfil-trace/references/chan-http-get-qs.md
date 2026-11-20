# Channel: HTTP GET query-string carry

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

GET exfil hides data in path/query. Histogram `-e http.request.full_uri` lengths; an outlier long tail of requests to one host is the tell. Decode per `misc-encoding-carrier` once the carrier bytes are extracted.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
