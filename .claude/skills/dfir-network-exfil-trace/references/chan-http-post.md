# Channel: HTTP POST/PUT upload

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

`http.request.method=="POST"`, `http.content_length`, per-URI count in `http_req,tree`, then `--export-objects http` for the bodies. The endpoint path is the claim; the exported bytes are the proof. Legit telemetry POSTs too — rank by volume and by how unusual the URI is for the bundle's baseline.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
