# Persistence misc: Startup folders

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`C:\Users\<u>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` (per-user) and `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp` (all users). `ls -la`; for `*.lnk`, `strings -a -el` gives target, volume serial and target MAC times (lnkinfo absent here). A raw .exe/.bat/.ps1 works too.

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
