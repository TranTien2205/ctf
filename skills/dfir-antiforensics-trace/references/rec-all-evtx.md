# Recovery: Destroyed: every EVTX incl Sysmon

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns: prefetch `.pf` (execution), `Amcache.hve` (execution), MPLog + DetectionHistory (Defender's own memory), SRUM + browser SQLite (activity counters). The lesson of the table: log clearing never reaches the non-log artifacts, so the execution story rebuilds from them.

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
