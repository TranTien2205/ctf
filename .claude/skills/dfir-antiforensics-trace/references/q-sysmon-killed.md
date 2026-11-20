# Question: Was Sysmon tampered with

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Sysmon 4 (service state, unfilterable) vs 16 (config change, unfilterable): 16-without-4 = config-only kill; 4 = service stop. Both survive configuration scrubbing.

## Evidence rule

Each question's answer is a named record: event id + field, journal
reason + name, or carved-region + hash. Quote the row.

## Pivot

`rec-*` for the survivor columns when the answering artifact was itself
destroyed.
