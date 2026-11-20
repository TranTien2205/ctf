# Scenario: Scenario: trail + S3 access logs

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Control plane from the trail (bucket opens, policy edits), object reads from the access log (the ONLY object-read record by default) - the two answer different halves of 'what happened to the bucket'.

## Exit

Ends with a quoted record + window bounds, or a recorded negative and
the next family named.

## Pivot

Done -> `work-*` for reporting discipline.
