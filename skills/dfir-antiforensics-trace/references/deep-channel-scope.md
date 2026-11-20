# Deep: Which channels carry which tamper events

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

1102 -> Security only; 104 -> every non-Security channel (System, Application, PowerShell, Sysmon as 'channel'); 1100 -> Security; 4719 -> Security; 6005/6006/703x -> System; Sysmon 4/16 -> Sysmon/Operational. The clear of ONE channel leaves the others' records — that's why the falsifier sweeps five ids across channels.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
