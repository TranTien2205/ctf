# Method: Dedup on eventID/sharedEventID

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Same call can appear in two trails (org + account) or twice on retry-delivery - dedupe on `eventID` before counting; `sharedEventID` joins the two-account view of one action.

## Discipline

Each method keeps the evidence rule: the answer is a quoted record;
the method only gets you to it.

## Pivot

Method spent -> `scen-*` for the bundle shape.
