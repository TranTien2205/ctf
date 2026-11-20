# Method: Every hive, every user

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

HKLM SOFTWARE (Run, IFEO, AppInit, policies), SYSTEM (services, BootExecute, LSA, print monitors, KnownDLLs), every NTUSER.DAT (HKCU Run, COM classes, screensaver, Office). One user-scope pass per user, not per machine.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.
