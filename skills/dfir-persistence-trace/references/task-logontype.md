# Scheduled task: LogonType field

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`<LogonType>`: `Password` (stored creds  -  the task runs whether the user logs on), `InteractiveToken` (only when that user is logged on), `S4U` (service-for-user  -  runs without stored creds, needs the right), `InteractiveTokenOrPassword`. InteractiveToken means the persistence fires only at that user's logon  -  narrows which NTUSER/logon events corroborate.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
