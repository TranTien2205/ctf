# Method: Gap evidence vs event evidence

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A 1102/104 names the clearer; a record-id gap only proves records vanished between two identifiers. The gap still needs the deleting mechanism found (surgical tool, corrupted chunk, collection truncation) — report the gap bounds and then hunt the mechanism before naming tampering.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
