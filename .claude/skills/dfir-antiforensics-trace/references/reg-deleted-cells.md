# Registry: Unallocated hive cells

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A deleted value's cell goes unallocated inside the hive but keeps its data until reused — raw hive carving finds 'deleted' values the official view hides. `hive_parse.py` covers live cells; unallocated-space carving is a manual hex pass.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
