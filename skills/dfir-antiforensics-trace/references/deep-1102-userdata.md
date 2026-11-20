# Deep: 1102 UserData, not EventData

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The clear event's fields live under `UserData/LogFileCleared`, not `EventData` — `evtx_query.py --answer` resolved SubjectUserName from inside UserData with no path given (measured). A hand-rolled parser looking only at EventData misses it.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
