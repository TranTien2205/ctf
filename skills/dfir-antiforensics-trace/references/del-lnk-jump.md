# Deletion: LNK/jump-list survival

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Opening a deleted file leaves its LNK in Recent items and jump lists — `tools/forensics/lnk_parse.py` reads them: target path, timestamps, sometimes volume serials. The file is gone; its shortcut history is not.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
