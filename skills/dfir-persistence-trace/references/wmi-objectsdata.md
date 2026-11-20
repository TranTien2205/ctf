# WMI: OBJECTS.DATA on-disk

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`C:\Windows\System32\wbem\Repository\OBJECTS.DATA`  -  needs `INDEX.BTR` and `MAPPING*.MAP` beside it to parse (SANS, Finding Evil WMI Event Consumers with Disk Forensics). No parser here: day-zero is `strings -a -n 8 OBJECTS.DATA | grep -iE 'EventFilter|EventConsumer|FilterToConsumer|SELECT .* FROM __Instance'`.

## Evidence rule

Quote `CommandLineTemplate`/`ScriptText` from the consumer AND show the
binding  -  consumer alone is payload debris without a live trigger.

## Pivot

WMI quiet -> startup folders / Office / BITS (`misc-*`), then Linux (`lnx-*`).
