# Trap: timeline_merge eats line 1

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Measured: headerless 4-record TSV -> rows_read 3, window 49s late. TIMECOL is a header NAME or 0-based index - a name on a headerless file gave parsed:0, unparsed:3, forced inconclusive. Emit the header.

## Guard

Check before the claim it protects - each trap is a way to produce a
plausible-looking wrong answer.

## Pivot

Traps clear -> `meth-*` for the next step.
