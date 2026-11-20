# Scheduled task: Trigger types that answer when

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

XML `<Triggers>`: `BootTrigger`, `LogonTrigger`, `CalendarTrigger`, `TimeTrigger`, `SessionStateChangeTrigger`, `EventTrigger` (on an event id  -  persistence that fires on a specific system event). The trigger kind decides which corroborating log shows the firing.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
