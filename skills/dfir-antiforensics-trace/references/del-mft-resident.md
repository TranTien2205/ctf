# Deletion: Resident $DATA recovery

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A small deleted file's content may survive IN the freed MFT record (resident $DATA, <~700 bytes). `tools/forensics/mft_parse.py` finds deleted records; the resident data area is the carve target. After sdelete -c this is gone — the MFT was filled.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
