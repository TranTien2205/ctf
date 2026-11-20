# Registry: Key LastWriteTime as the clock

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A registry key's last-written timestamp is kernel-maintained and not user-settable — the untamperable clock for 'when was this key touched'. `tools/forensics/hive_parse.py` reads it; it survives value-level edits.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
