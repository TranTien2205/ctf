# GuardDuty: Severity bands

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Low 1.0-3.9, Medium 4.0-6.9, High 7.0-8.9, Critical 9.0-10.0 - a numeric `severity`, not a word; report the number with the band.

## Evidence rule

A finding opens a window; the answer still comes from a quoted
CloudTrail or flow record inside it.

## Pivot

Window known -> back to `api-*` on the trail, or `vpc-*` on flows.
