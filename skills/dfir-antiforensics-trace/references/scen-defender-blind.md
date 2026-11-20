# Scenario: Defender quiet during the window

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Expected detections that never appear: check exclusion keys (non-policy first), 5007 New value for exclusion paths, 5001/5010/5012 disable events, 1013 history purge, MPLog for what the engine still saw. 5013 presence means the tamper failed.

## Evidence rule

The scenario names the record chain; every link still needs its verbatim
quote through post-probe.

## Pivot

Chain breaks -> the rec-* column for whatever was destroyed.
