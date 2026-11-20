# Method: inventory first

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`artifact_inventory.py --path <dir>` files CloudTrail shapes as `cloudtrail-json` (path or eventVersion+eventSource+Records head); S3 access logs, flow logs and findings measured landing in `unknown` - name them yourself.

## Discipline

Each method keeps the evidence rule: the answer is a quoted record;
the method only gets you to it.

## Pivot

Method spent -> `scen-*` for the bundle shape.
