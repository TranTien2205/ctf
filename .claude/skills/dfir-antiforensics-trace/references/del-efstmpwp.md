# Deletion: EFSTMPWP — cipher /w signature

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`cipher.exe /w:<dir>` wipes free space by writing a temp file named `EFSTMPWP` at the volume root (fills, deletes, repeats). A leftover EFSTMPWP in $MFT/$J records names the wipe; layout at `skills/ctf-forensics/windows.md:548-566`.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
