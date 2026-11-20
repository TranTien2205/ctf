# Recovery: Destroyed: one file

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns: Sysmon 23 archive under `C:\Sysmon` (the bytes), $Recycle.Bin $I/$R (path + deletion time + bytes), $J 0x200 (deletion record), unallocated $MFT record/resident $DATA (name+times+maybe content).

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
