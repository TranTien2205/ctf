# Channel: TLS volume without decryption

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

Encrypted channel still leaks volume + cadence + destination: `tls.record.length` summed per stream, `tls.handshake.extensions_server_name` for the claimed name, `ip.dst` for the truth. The size question is answerable without the keylog; the content question is not.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
