# Tool route: pandas 2.3.3

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Present here. `read_csv(sep='\t', dtype=object)` - dtype is not optional; `to_datetime(utc=True)` for eventTime; sort_values for window order.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
