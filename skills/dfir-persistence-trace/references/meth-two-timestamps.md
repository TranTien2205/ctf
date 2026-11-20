# Method: Two-timestamp corroboration

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

A mechanism claim pairs the RECORD (7045 ts, XML <Date>, key lastChange) with an EXECUTION artifact (DynamicInfo ftLastRun, 200/201 events, Prefetch). A mechanism dated only by registration has not proven firing; an execution with no registration has not proven persistence.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.
