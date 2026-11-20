# Edge: Corruption vs surgical deletion

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Damaged chunk magic (not ElfChnk) inside the file marks corruption/carve-boundary, not deletion — identifier gaps only count across VALID neighbouring chunks.

## Pivot

`corpus-index.md`; `meth-falsifier` when every shape is benign.
