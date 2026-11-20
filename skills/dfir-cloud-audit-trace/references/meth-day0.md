# Method: Day-zero pipeline

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

aws CLI ABSENT - day zero is `find -exec gzip -dc {} +` | jq | sort | head, then the same rows into a headered TSV for pandas: `pandas.read_csv(sep='\t', dtype=object)`, `to_datetime(utc=True)`, `sort_values`. Emit the header - timeline_merge eats line 1.

## Discipline

Each method keeps the evidence rule: the answer is a quoted record;
the method only gets you to it.

## Pivot

Method spent -> `scen-*` for the bundle shape.
