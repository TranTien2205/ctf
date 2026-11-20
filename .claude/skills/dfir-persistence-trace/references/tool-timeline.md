# Tool route: timeline_merge.py

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`python3 tools/forensics/timeline_merge.py`  -  joins the mechanism's record timestamp with execution artifacts into one ordered view; the 'when did it persist and when did it fire' answer.

## Evidence rule

Tool output is the excerpt to quote; the record field inside it is the
evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
