# Registry: 0x9F duplicate names

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Duplicate value names built on character 0x9F: distinct under Latin-1, colliding under Windows-1252 — a value 'twins' hiding in plain sight depending on the reader's codepage (dfir.ru).

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
