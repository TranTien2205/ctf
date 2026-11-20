# Question: Was the PowerShell history deleted

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`%AppData%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt` deletion leaves a $J 0x200 naming it (T1070.003) — the delete record IS the answer to 'was history wiped'.

## Evidence rule

Each question's answer is a named record: event id + field, journal
reason + name, or carved-region + hash. Quote the row.

## Pivot

`rec-*` for the survivor columns when the answering artifact was itself
destroyed.
