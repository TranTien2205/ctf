# Tool route: timeline_merge.py

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`--source trail.tsv:eventTime:cloudtrail` - header REQUIRED (line 1 eaten); TIMECOL name or 0-based index; merges the cloud rows beside host artifacts.

## Evidence rule

Tool output is the excerpt; the record field inside it is the evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
