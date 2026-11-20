# Recovery: Destroyed: Security log

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns in order: Sysmon/Operational (a different channel, cleared separately), prefetch + Amcache (execution survived), $J 0x100/0x200 (file ops survived), a shadow copy's older Security.evtx (the same channel, earlier). Work the columns in order; each is one probe.

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
