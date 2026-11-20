# Recovery: Destroyed: timestamps changed

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns: $FILE_NAME (the untouched set), $J 0x8000 (the change record), Sysmon 2 `PreviousCreationUtcTime` (the real value recorded at change time), prefetch run times / key last-written (independent clocks).

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
