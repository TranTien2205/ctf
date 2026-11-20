# Deletion: Sysmon 26 — FileDeleteDetected

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Same event family but NOT archived — logged only. A bundle with 26 and no 23 means the deletion events exist and the file bytes do not; the answer is then 'what was deleted' (name+hashes) not 'the file itself'.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
