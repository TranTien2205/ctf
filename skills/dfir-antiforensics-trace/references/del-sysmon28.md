# Deletion: Sysmon 28 — FileBlockShredding

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

'detects and blocks file shredding from tools such as SDelete' — names the shredder binary itself (Microsoft Learn, Sysmon). The blocked attempt is the finding: shredding was attempted AND stopped.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
