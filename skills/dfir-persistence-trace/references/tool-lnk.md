# Tool route: lnk_parse.py

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`python3 tools/forensics/lnk_parse.py <file>.lnk`  -  target path + internal MAC stamps; `strings -a -el` is the fallback.

## Evidence rule

Tool output is the excerpt to quote; the record field inside it is the
evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
