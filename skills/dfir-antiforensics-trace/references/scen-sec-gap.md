# Scenario: A Security.evtx with a gap

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Symptom: questions reference events that aren't in the converted records. Path: record-id probe first (gap bounds + count), then the clear sweep (1102/104/1100) to separate clear from surgical delete, then rec-sec survivors for the lost window. The gap bounds date the hole; the 1102 (if present) names who.

## Evidence rule

The scenario names the record chain; every link still needs its verbatim
quote through post-probe.

## Pivot

Chain breaks -> the rec-* column for whatever was destroyed.
