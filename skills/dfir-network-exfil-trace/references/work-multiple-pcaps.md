# Workflow: Multiple captures in one bundle

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Per-capture first pass (`capinfos` window for each), order them on the timeline, then treat peer questions per-window: a peer only in the later capture is a different answer than a peer spanning both. `timeline_merge.py` takes each capture's fields as its own --source.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
