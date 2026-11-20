# GuardDuty: DetectionMechanism caveat

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`.Custom` = fired off YOUR uploaded threat list, `.Reputation` = a domain-reputation model - neither is independent corroboration of maliciousness; treat them as pointers to the underlying records.

## Evidence rule

A finding opens a window; the answer still comes from a quoted
CloudTrail or flow record inside it.

## Pivot

Window known -> back to `api-*` on the trail, or `vpc-*` on flows.
