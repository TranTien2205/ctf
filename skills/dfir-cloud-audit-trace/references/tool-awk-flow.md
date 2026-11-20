# Tool route: awk on flow logs

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

14 default fields, space-split SAFE (no bracketed/quoted fields in the default format): `$13 action`, `$10 bytes`, `$5 dstaddr`, `$11/$12 start/end`.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
