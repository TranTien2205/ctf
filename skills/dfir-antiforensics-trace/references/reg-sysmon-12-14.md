# Registry: Sysmon 12/13/14 registry events

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

12 key create/delete, 13 value set, 14 key/value rename — the event-side record of registry tampering with `ProcessGuid` attribution. When the hive itself was wiped, these events may be the only record of what was set.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
