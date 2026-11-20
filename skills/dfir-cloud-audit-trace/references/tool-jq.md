# Tool route: jq 1.8.1

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Present here. The day-zero swiss knife: decompress -> '.Records[] | [fields] | @tsv'. @tsv needs ARRAYS; object input exits 5.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
