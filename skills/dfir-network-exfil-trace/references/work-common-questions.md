# Workflow: The recurring question set

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Across published Sherlock/DFIR sets, the recurring shapes are: volume out, peer identity, first-seen time, process name, file name/content, channel type, cadence. Each maps to a `q-*` module — the map exists because re-deriving the route per question is where sessions burn the budget.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
