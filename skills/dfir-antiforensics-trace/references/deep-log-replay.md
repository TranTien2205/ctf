# Deep: Transaction-log replay ordering

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Recovery applies entries earliest-first across BOTH .LOG1 and .LOG2 on Win8.1+ — the logs alternate as active write targets, so a single-log replay can restore a stale state: .LOG1 alone can show the value present when .LOG2 later deleted it. Replay order is the correctness condition, not a detail.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
