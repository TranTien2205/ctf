# Persistence misc: Office COM add-ins

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

HKCU or HKLM `Software\Microsoft\Office\<app>\Addins\<name>`  -  `LoadBehavior`=3 means load at startup (0/2 = off). The add-in DLL is the payload; the LoadBehavior is the switch.

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
