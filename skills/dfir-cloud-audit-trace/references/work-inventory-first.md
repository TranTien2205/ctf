# Workflow: Inventory first

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`artifact_inventory.py --path <dir>` before any claim - the CloudTrail shapes land in `cloudtrail-json`; S3/flow/finding shapes land in `unknown` and are named manually. Absence claims need the artifact list.

## Pivot

Workflow covered -> `scen-*` for the bundle shape.
