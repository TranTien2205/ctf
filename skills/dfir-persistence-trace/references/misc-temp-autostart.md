# Persistence misc: Autostart pointing at temp/writable dirs

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Any mechanism whose value points into `%TEMP%`, `C:\Users\Public`, `%LOCALAPPDATA%\Temp`, `C:\ProgramData` roots, or a user-writable path is the higher-signal row  -  a legitimate binary can update but a binary whose sole location is a world-writable dir is the candidate shape.

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
