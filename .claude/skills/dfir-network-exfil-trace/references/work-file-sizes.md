# Workflow: Sizing expectations

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A 5MB pcap is a few thousand packets — sub-second taps. Multi-GB captures need `editcap` windowing or `-Y` pre-filters before taps. SRUDB.dat is tens of MB; eve.json in big bundles is hundreds of MB — stream with jq `--stream` or grep event_type first.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
