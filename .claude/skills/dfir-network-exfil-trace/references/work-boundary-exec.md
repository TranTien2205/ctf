# Workflow: Boundary: execution vs exfil

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`dfir-execution-trace` answers 'what ran' — Sysmon 1/4688 CommandLine, Prefetch, Amcache. THIS class answers 'what left'. The join key is `ProcessGuid`/`Application`: flow evidence + process evidence together make 'process X exfiltrated Y bytes'. Neither class alone says the full sentence.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
