# Question: How many records vanished and when

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Gap (a,b) in identifiers: count = b-a-1 records; the window is bounded by the FILETIMEs of records a and b. Quote both bounds plus the count — all three come from the same probe output.

## Evidence rule

Named artifact + named field + verbatim quote — the class contract.

## Pivot

The answering artifact destroyed -> `rec-*` columns.
