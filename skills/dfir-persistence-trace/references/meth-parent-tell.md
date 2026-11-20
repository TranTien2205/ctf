# Method: Parent-process tell

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

The loader names the mechanism even when the record is gone: svchost -k / taskeng.exe / Task Scheduler host = task; services.exe / svchost = service; explorer.exe at logon = Run/startup folder; wmiprvse.exe = WMI consumer; winlogon = screensaver/Winlogon values. Sysmon 1 `ParentImage` is the join.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.
