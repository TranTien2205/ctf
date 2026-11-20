# Cookbook: Query rate per second

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`-z io,stat,1,"COUNT(dns.qry.name)dns.qry.name"` — the burst shape; fixture peaked at 3/s here.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
