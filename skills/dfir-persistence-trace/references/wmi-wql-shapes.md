# WMI: WQL trigger shapes

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`SELECT * FROM __InstanceCreationEvent WITHIN <sec> WHERE TargetInstance ISA 'Win32_<x>'`  -  polling triggers (WITHIN = interval). Timer: `__TimerEvent` / `Win32_LocalTime`/`UTCTime`. Logon: `TargetInstance ISA 'Win32_LogonSession'`. Process-start: `Win32_ProcessStartTrace`. The WQL text is the trigger record.

## Evidence rule

Quote `CommandLineTemplate`/`ScriptText` from the consumer AND show the
binding  -  consumer alone is payload debris without a live trigger.

## Pivot

WMI quiet -> startup folders / Office / BITS (`misc-*`), then Linux (`lnx-*`).
