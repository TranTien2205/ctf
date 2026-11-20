# Workflow: When carving is worth it

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Carve for: quarantine payloads, resident $DATA, unallocated hive cells, unallocated MFT records. Do NOT carve for: wiped files (bytes are gone), cleared channels (the file was reset), overwritten journal regions.

## Pivot

`question-map.md`; `../SKILL.md` Discipline for the three-attempts rule.
