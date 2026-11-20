# Tool route: evtx_query.py

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`python3 tools/forensics/evtx_query.py --input <log>.jsonl --event-id <id> --order asc --challenge <n> --class dfir-persistence-trace --evidence-kind class --answer <field>`  -  the sanctioned event read; `--answer` prints the pre-flag argv. Ids for this class: 7045/7034/7036/7040, 4697/4698-4702, 106/140/141/200/201/129, Sysmon 1/11/13/19/20/21, WMI-Activity 5857-5861, Bits-Client 3/4/59/60.

## Evidence rule

Tool output is the excerpt to quote; the record field inside it is the
evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
