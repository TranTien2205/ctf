# Recovery: Destroyed: registry value

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns: `.LOG1`/`.LOG2` replay (deleted values live in the transaction logs — BOTH logs on Win8.1+), unallocated hive cells, shadow copy of the hive, Sysmon 12/13/14 (the event-side record).

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
