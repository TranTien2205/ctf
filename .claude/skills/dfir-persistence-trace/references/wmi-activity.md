# WMI: WMI-Activity/Operational events

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`Microsoft-Windows-WMI-Activity/Operational`: **5861** Operation_ESStoConsumerBinding  -  the binding itself, the record that names the persistence; **5860** Operation_TemporaryEssStarted; **5857** Operation_Started (provider loaded); **5858** Operation_ClientFailure carrying the failing WQL and result code (repnz/etw-providers-docs).

## Evidence rule

Quote `CommandLineTemplate`/`ScriptText` from the consumer AND show the
binding  -  consumer alone is payload debris without a live trigger.

## Pivot

WMI quiet -> startup folders / Office / BITS (`misc-*`), then Linux (`lnx-*`).
