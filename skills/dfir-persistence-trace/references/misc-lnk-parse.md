# Persistence misc: Startup .lnk reading

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`strings -a -el` on a .lnk: UTF-16 strings carry the target path, plus volume serial and target MAC times baked into the LNK structure  -  a .lnk in Startup whose internal MAC timestamps pre-date its file-system placement is the 'copied-in' shape. `tools/forensics/lnk_parse.py` is the in-tree parser.

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
