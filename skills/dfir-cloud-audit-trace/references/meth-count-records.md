# Method: Count records, not files

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`.Records | length` summed across files - file count says delivery batches, record count says activity. The first probe prints a TSV to bound, not a verdict.

## Discipline

Each method keeps the evidence rule: the answer is a quoted record;
the method only gets you to it.

## Pivot

Method spent -> `scen-*` for the bundle shape.
