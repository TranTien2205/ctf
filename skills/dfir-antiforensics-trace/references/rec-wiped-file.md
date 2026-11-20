# Recovery: Destroyed: wiped file

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Stop carving the file — it's gone. Columns: $MFT name and times (metadata survives wiping), quarantine `ResourceData` (if Defender held it), LNK/jump lists (usage history), MPLog `MaxTimeFile` (Defender touched it).

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
