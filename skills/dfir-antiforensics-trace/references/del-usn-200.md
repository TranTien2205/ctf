# Deletion: $J reason 0x200 FILE_DELETE

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Deletion record in the USN journal — fires whether or not the Recycle Bin was used (shift-delete, API delete). Pair with the 0x1000/0x2000 rename records for the sdelete shape.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
