# Question: Which shredder ran

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Sysmon 28 names it directly; else the $J burst shape (26 = SDelete), EFSTMPWP (cipher), or the EulaAccepted key (SDelete under that SID).

## Evidence rule

Named artifact + named field + verbatim quote — the class contract.

## Pivot

The answering artifact destroyed -> `rec-*` columns.
