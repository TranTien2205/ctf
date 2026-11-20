# Workflow: Re-running probes safely

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Reads are idempotent — re-running a tap costs time only. Exports overwrite their target dir; use a fresh `ex/` per pass. The only state that matters is the ledger's: record each result once through post-probe rather than re-running to remember.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
