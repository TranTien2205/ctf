# Workflow: Evidence kind

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

CloudTrail/S3/flow records are `--evidence-kind class`; a flag-shaped string inside a record field is a candidate until `pre-flag`. Nothing here is a verdict by itself.

## Pivot

Workflow covered -> `scen-*` for the bundle shape.
