# Method: Mechanism sweep order

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Cost-ordered: (1) 7045 System  -  one query, almost always present; (2) Tasks\ XML glob  -  file system, no parser; (3) Run-family hives via registry-read.py; (4) TaskCache DynamicInfo; (5) WMI OBJECTS.DATA strings; (6) startup folders/Office/BITS; (7) Linux/macOS only when the bundle is not Windows. The sweep ends at the falsifier, not the first find.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.


## Closing note

Record the reading, not the impression: the corpus exists so that a
verbatim record or a recorded negative  -  not a hunch  -  ends each probe.
