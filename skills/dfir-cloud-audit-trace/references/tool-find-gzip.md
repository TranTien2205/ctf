# Tool route: find -exec gzip -dc

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`find . -name '*.json.gz' -exec gzip -dc {} +` - NOT zcat ** (globstar trap). The decompressor for a whole trail.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
