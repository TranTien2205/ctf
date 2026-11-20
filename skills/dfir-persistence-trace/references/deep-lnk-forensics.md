# Deep dive: Deep: LNK internal timestamps

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

A .lnk carries target MAC times from when the link was BUILT  -  a lnk whose internal stamps predate its own file creation is the copied-in shape; `tools/forensics/lnk_parse.py` or `strings -a -el` surfaces them.

## Use

Depth for when the row-level module is not enough  -  cite this file's
artifact and offset when the claim rests on the decoded detail.

## Pivot

Deep read done -> back to the scenario (`scen-*`) or the matrix.
