# Tool route: artifact_inventory.py

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Files CloudTrail shapes as `cloudtrail-json`; S3 access logs/flow logs/findings measured landing in `unknown` - name them manually.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
