# Question: Is the deleted sample recoverable

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Quarantine ResourceData -> RC4 -> carve bsd+0x14 -> hash; or Sysmon 23 archive `C:\Sysmon`; or $Recycle.Bin $R. The recovery column depends on which artifact family recorded the file.

## Evidence rule

Each question's answer is a named record: event id + field, journal
reason + name, or carved-region + hash. Quote the row.

## Pivot

`rec-*` for the survivor columns when the answering artifact was itself
destroyed.
