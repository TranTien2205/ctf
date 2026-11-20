# WMI: WMI subscription = three objects

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

A permanent subscription fires only if ALL THREE exist: `__EventFilter` (the WQL trigger), an `__EventConsumer` subclass  -  `CommandLineEventConsumer` (`CommandLineTemplate` = the payload) or `ActiveScriptEventConsumer` (`ScriptText`)  -  and `__FilterToConsumerBinding` joining them. Finding one object without the binding is debris, not live persistence.

## Evidence rule

Quote `CommandLineTemplate`/`ScriptText` from the consumer AND show the
binding  -  consumer alone is payload debris without a live trigger.

## Pivot

WMI quiet -> startup folders / Office / BITS (`misc-*`), then Linux (`lnx-*`).
