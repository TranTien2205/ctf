# Persistence misc: BITS persistence

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Queue `C:\ProgramData\Microsoft\Network\Downloader\qmgr.db` (ESE; `esedbexport` measured absent)  -  day-zero `strings -a -el qmgr.db | grep -iE 'http|\.exe'`. Log channel `Microsoft-Windows-Bits-Client/Operational`: **3** Job Created (Job ID, name, `Process Path`, `Owner`), **59/60** Started/Stopped (carry the transfer URL), **4** Job Completed. BITS jobs auto-resume  -  a download job that also `SetNotifyCmdLine`s a binary is persistence; 61 is UNVERIFIED here.

## Evidence rule

The file or value is the record  -  quote its content; existence plus a
suspicious-but-unnamed file is a candidate.

## Pivot

Misc surfaces quiet -> Linux (`lnx-*`) or the matrix (`mx-*`) for the next
family.
