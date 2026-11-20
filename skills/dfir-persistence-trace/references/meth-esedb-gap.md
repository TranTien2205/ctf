# Method: ESE store gap

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`esedbexport` measured absent  -  qmgr.db (BITS) and OBJECTS.DATA (WMI, its own format but same 'no parser' posture) get strings-first triage: `strings -a -el/-n 8` for URLs, paths, WQL fragments. A strings hit is a candidate needing the field record, not a finding.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.
