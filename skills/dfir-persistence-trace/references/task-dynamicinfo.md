# Scheduled task: DynamicInfo offsets

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`DynamicInfo` binary value  -  the only place last-run time lives in the registry (cyber.wtf, Windows Registry Analysis - Tasks; libyal winreg-kb corroborates the same offsets independently): magic DWORD at 0 (currently 0x3), `ftCreate` FILETIME at 4, `ftLastRun` at 12, `dwTaskState` DWORD at 20, `dwLastErrorCode` DWORD at 24, `ftLastSuccessfulRun` at 28  -  absent on Vista/7, so the blob is 28 or 36 bytes. Decode with a 6-line struct unpack (the SKILL.md snippet).

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
