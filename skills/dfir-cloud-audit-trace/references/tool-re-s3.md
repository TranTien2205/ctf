# Tool route: S3 log regex

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`re.findall(r'\[[^\]]*\]|"[^"]*"|\S+', line)` - 27 fields; naive split gives 30. awk works only on fields without spaces.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
