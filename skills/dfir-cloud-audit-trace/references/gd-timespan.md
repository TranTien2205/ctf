# GuardDuty: eventFirstSeen/eventLastSeen/count

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`service.eventFirstSeen`, `service.eventLastSeen`, `service.count` bound the finding's window and repetition - the fields to quote for 'when' and 'how many times'.

## Evidence rule

A finding opens a window; the answer still comes from a quoted
CloudTrail or flow record inside it.

## Pivot

Window known -> back to `api-*` on the trail, or `vpc-*` on flows.
