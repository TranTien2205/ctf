# Cookbook: Filter arithmetic

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`dns.qry.name.len > 50` works because .len is numeric; comparing `frame.len > 1000 and udp` chains fine. `!x` and `not x` both negate — but `!=` on a field that exists in BOTH directions surprises: `ip.src != H` still matches packets where the OTHER direction's src equals H inside multi-value fields.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
