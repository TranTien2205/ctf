# Question: Was the logging/AV service stopped

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Sysmon 4 (State=Stopped), 6005/6006, 7034/7035/7036 for EventLog/Sysmon64, Defender 5001/5010/5012 — plus the 4609 reboot check.

## Evidence rule

Each question's answer is a named record: event id + field, journal
reason + name, or carved-region + hash. Quote the row.

## Pivot

`rec-*` for the survivor columns when the answering artifact was itself
destroyed.
