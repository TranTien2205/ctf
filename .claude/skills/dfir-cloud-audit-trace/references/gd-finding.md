# GuardDuty: GuardDuty finding shape

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

lowerCamelCase JSON keys (EventBridge reads `$.detail.severity`, `$.detail.type`). A finding is a SUMMARY - it points you at a window; the CloudTrail record inside it is the evidence.

## Evidence rule

A finding opens a window; the answer still comes from a quoted
CloudTrail or flow record inside it.

## Pivot

Window known -> back to `api-*` on the trail, or `vpc-*` on flows.
