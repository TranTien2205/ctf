# Scenario: Scenario: Windows bundle, question open

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Shape: hives + evtx + Tasks\ dir. Route: inventory -> 7045 -> Tasks XML glob -> Run hives -> TaskCache DynamicInfo -> WMI strings -> startup/Office/BITS -> falsifier check. Each stop writes its negative before moving.

## Exit condition

Each scenario ends with either a verbatim record quoted, or a recorded
negative and the next family named.

## Pivot

Scenario done -> `work-*` for the reporting discipline.


## Closing note

Record the reading, not the impression: the corpus exists so that a
verbatim record or a recorded negative  -  not a hunch  -  ends each probe.
