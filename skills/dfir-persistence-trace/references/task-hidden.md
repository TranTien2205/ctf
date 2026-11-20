# Scheduled task: Hidden tasks

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`<Hidden>` in the XML flags the task invisible to mmc's Task Scheduler snap-in but NOT to the file system or `schtasks /query` with the right flags  -  a hidden flag is itself a mild signal worth recording.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
