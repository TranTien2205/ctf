# Cookbook: Long+hex query names

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`-Y 'dns.qry.name.len > 50 and dns.qry.name matches "^[0-9a-f]{16,}[.]"'` — the [.] escape is required on tshark 4.0.7. Pair length with alphabet; alone each over-matches.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
