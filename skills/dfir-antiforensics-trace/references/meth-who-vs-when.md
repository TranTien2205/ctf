# Method: Who cleared vs when cleared

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

1102 carries both: SubjectUserName (who) + its own timestamp (when cleared). The gap carries neither — pairing the gap with a tool execution record (Sysmon 1/4688) is the attribution path.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
