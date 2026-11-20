# Persistence misc: PowerShell profile persistence

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`$PROFILE` paths  -  `WindowsPowerShell\profile.ps1` (all hosts, current user), `Microsoft.PowerShell_profile.ps1`, host-specific variants, and the AllUsers copies under `C:\Windows\System32\WindowsPowerShell\v1.0\`. A profile file that exists is worth reading  -  it runs on every console start.

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
