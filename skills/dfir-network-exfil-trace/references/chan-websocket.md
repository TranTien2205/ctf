# Channel: WebSocket channel

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Long-lived 101-upgraded connection inside HTTP/443. `io,phs` may only show `websocket`/`data` frames; `follow,tcp` shows the frame flow. Volume question -> `conv,tcp`/`tls.record.length`; content needs the unmasked frames (client-to-server WS frames are XOR-masked).

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
