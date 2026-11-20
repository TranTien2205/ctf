# Scheduled task: TaskScheduler/Operational events

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

106 registered, 140 updated, 141 deleted (channel: Microsoft-Windows-TaskScheduler/Operational). Execution: **200** action started, **201** action completed (carries result code), **129** created task process  -  129 is the record that names the spawned process, the parentage proof.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
