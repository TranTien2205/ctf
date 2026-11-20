# Deep: When they disagree

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Three cases: fronting (inner host differs), ECH (outer is a cover name), stale SNI (CDN edge serving many tenants). Only `ip.dst` is observation in all three — the report names the claim and the observation separately.

## Evidence rule

The deep card refines interpretation; the quotable row still comes from the base question's own probe.

## Pivot

`q-sni-vs-dst.md` for the procedure; `meth-answer-shape` for the reporting checklist.
