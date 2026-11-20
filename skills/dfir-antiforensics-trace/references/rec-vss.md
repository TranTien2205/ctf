# Recovery: Destroyed: shadow copies

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns: the command line in Sysmon 1/4688 (vssadmin/diskshadow), System 7036 for the VSS service, $J on the diff-area files, Amcache for `vssadmin.exe`.

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
