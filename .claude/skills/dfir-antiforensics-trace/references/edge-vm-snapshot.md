# Edge: VM snapshot reverts

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A restored VM snapshot makes logs 'lose' records that never existed in this timeline — indistinguishable from deletion by identifier gaps alone; look for snapshot tooling in the bundle or the odd next_id wrap.

## Pivot

`corpus-index.md`; the falsifier block for clean bundles.
