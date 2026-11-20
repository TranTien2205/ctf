# Scheduled task: TaskCache  -  the registry twin

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

SOFTWARE `Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\<path>` value `Id` = the task GUID; `...\TaskCache\Tasks\{GUID}` carries `Path`, `Actions`/`Triggers` (binary blobs), `DynamicInfo`, `Hash`, `SecurityDescriptor` in SDDL  -  the SDDL is what still answers *which account* after the XML is deleted. Sibling subkeys `Boot`, `Logon`, `Plain` each hold only an `Id` back into Tasks; a `Maintenance` subkey and `URI` value are UNVERIFIED here.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
