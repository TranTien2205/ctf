# Method: Replicate the mechanism read

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

No hive parser beyond registry-read.py here  -  replicate the read the tool makes: hive root is the mount point (drop HKLM prefix), replay LOG1/LOG2 before trusting values, r+b permission needed, `regf` magic check before blaming absence. The error shapes are in `../SKILL.md` traps.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.
