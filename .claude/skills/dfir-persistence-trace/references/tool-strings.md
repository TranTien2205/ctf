# Tool route: strings discipline

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`strings -a -el` UTF-16 for Windows binaries/hives/OBJECTS.DATA/qmgr.db; `-n 8` minimum to cut noise; a strings hit is a candidate  -  the structured record is still required.

## Evidence rule

Tool output is the excerpt to quote; the record field inside it is the
evidence.

## Pivot

Tool covered -> `tool-inventory` for the next family.
