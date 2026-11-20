# Tool route: aws CLI is ABSENT

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`aws cloudtrail lookup-events` is not the day-zero route - bundles are offline anyway; jq+pandas carry the whole job.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
