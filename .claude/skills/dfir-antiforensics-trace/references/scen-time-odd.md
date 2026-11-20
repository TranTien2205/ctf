# Scenario: Times that don't line up

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

$SI says the file predates the OS; $FN says created during the window -> Sysmon 2 PreviousCreationUtcTime settles it. The sub-second tell (.0000000 vs real ticks) corroborates a formatted-string plant.

## Evidence rule

The scenario names the record chain; every link still needs its verbatim
quote through post-probe.

## Pivot

Chain breaks -> the rec-* column for whatever was destroyed.
