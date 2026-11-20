# Method: The quotable shape

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Every answer carries artifact + field: `1102 SubjectUserName`, `104 Channel`, `5007 New value`, chunk gap `(4200,4310)`, `$I` original path + deletion FILETIME. A bare name or timestamp with no artifact named is not an answer — the Discipline section in ../SKILL.md is the contract.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
