# Edge: Size vs retention mismatch

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A channel far below its configured max-size that shows oldest records is consistent with clearing OR low activity — the next_id vs oldest arithmetic distinguishes: next_id near oldest+count means contiguous history, not wrap.

## Pivot

`corpus-index.md`; the falsifier block for clean bundles.
