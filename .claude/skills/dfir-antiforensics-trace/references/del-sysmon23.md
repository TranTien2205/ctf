# Deletion: Sysmon 23 — FileDelete (archived)

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The deleted file is COPIED into `ArchiveDirectory` ('Name of directories at volume roots', default `Sysmon` -> `C:\Sysmon`) before removal. Fields: `TargetFilename`, `Image`, `Hashes`, `IsExecutable`, `Archived`. The archive means the BYTES survive — recover and hash them.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
