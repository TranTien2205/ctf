# Cookbook: TLS ClientHello to peer

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`-Y 'tls.handshake.type==1 and ip.dst==PEER' -e tls.handshake.extensions_server_name` — the claim vs the observation in one row.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
