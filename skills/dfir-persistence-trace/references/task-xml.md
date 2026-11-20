# Scheduled task: Task XML  -  the payload record

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`C:\Windows\System32\Tasks\<folder>\<name>`  -  extensionless XML. Fields that answer: `<Command>`, `<Arguments>`, `<UserId>`, `<LogonType>`, `<Triggers>` (boot/logon/calendar), `<Hidden>`, `<Author>`, `<Date>` (REGISTRATION time, not execution). `grep -rl '<Command>' Tasks/ | xargs grep -h -A1 '<Command>'` harvests every command in one pass.

## Evidence rule

XML gives the command; TaskCache gives the GUID and the account; DynamicInfo
gives the run times; Security/Operational events give registration and firing.
Each artifact answers a different part  -  name which one the claim rests on.

## Pivot

Tasks clean -> services (`svc-*`) and WMI (`wmi-*`).
