# Workflow: Non-pcap snapshots in a bundle

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A captured `ss -tunap`, a `conntrack -L` dump, a firewall table export: all point-in-time. They corroborate a flow's existence at capture instant; they cannot carry volume or history — say exactly which instant each bound.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
