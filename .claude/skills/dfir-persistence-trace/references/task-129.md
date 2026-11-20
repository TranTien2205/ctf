# Scheduled task: Event 129  -  the spawned-process record

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

TaskScheduler/Operational 129 'created task process' carries the process name AND PID the task action launched  -  the record that joins the XML `<Command>` to an actual execution. Pair with Sysmon 1 ParentImage=`taskeng.exe`/svchost for corroboration.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
