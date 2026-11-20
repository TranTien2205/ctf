# Workflow: Knowing the class is done

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The class is finished when every question has a quoted record or a quoted falsifier — not when probes run out. `decide.py` owns the call; this module is the readiness check: each question mapped, each answer sourced, each negative recorded.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
