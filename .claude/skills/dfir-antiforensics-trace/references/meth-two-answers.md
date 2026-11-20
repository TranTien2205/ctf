# Method: Every erase question has two answers

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

'When did the erasure happen' (an event or a gap) and 'what survived it' (the recovery table). CONFIRM THE FIRST before spending a probe on the second — a missing log might be collection scope, and the recovery hunt is wasted when nothing was ever erased.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.
