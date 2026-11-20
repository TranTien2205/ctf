# Deletion: $Recycle.Bin $I/$R pairs

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`$Recycle.Bin\<SID>\$I<random>` metadata + `$R<random>` content. The $I holds the original path and the deletion FILETIME — the two-answer record: WHERE it was and WHEN it was deleted. Tools: `tools/forensics/recycle_i.py` parses $I records, `info2.py` the pre-Vista variant. A deleted $R with no $I is incomplete evidence — quote the $I row.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
