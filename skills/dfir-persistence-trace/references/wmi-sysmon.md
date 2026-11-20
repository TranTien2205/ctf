# WMI: Sysmon 19/20/21

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Sysmon **19** WmiEventFilter, **20** WmiEventConsumer, **21** WmiEventConsumerToFilter (the binding). Three separate event ids because the objects are separate  -  a live subscription usually shows all three.

## Evidence rule

Quote `CommandLineTemplate`/`ScriptText` from the consumer AND show the
binding  -  consumer alone is payload debris without a live trigger.

## Pivot

WMI quiet -> startup folders / Office / BITS (`misc-*`), then Linux (`lnx-*`).
