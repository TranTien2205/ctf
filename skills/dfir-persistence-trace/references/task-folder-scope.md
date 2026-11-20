# Scheduled task: Tasks\ subfolder taxonomy

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Standard folders: `\Microsoft\Windows\<feature>` are OS-owned  -  a non-Microsoft task at root level or a foreign folder name is the anomaly shape. Compare against a same-build baseline when the question is 'is this task stock'.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
