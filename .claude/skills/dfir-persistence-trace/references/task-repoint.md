# Scheduled task: Repoint trap  -  4702 not 4698

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Editing an existing task's action emits 4702 (updated), NOT 4698  -  and the XML `<Date>` still shows the ORIGINAL registration. A `<Date>` far from `DynamicInfo` `ftCreate` is timestomping  -  see deep-dives in `../dfir-antiforensics-trace/`.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
