# Scenario: A named file that is gone

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Question asks a property of a file the bundle lacks. Recovery order: Sysmon 23 archive -> $Recycle.Bin $I/$R -> $J 0x200 -> unallocated $MFT. If all four dry, the file may never have been in the bundle — collection scope first.

## Evidence rule

The scenario names the record chain; every link still needs its verbatim
quote through post-probe.

## Pivot

Chain breaks -> the rec-* column for whatever was destroyed.
