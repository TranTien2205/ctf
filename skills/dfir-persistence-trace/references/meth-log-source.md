# Method: Which channel proves which step

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

System 7045/7034/7036/7040 = service install+lifecycle; Security 4697/4698-4702 = install records (needs audit subcategories); TaskScheduler/Operational 106/140/141/200/201/129 = task registration+execution; WMI-Activity 5861/5857-5858+Sysmon 19-21 = WMI subscription; Bits-Client 3/4/59/60 = BITS jobs. Route the question to the channel that ANSWERS it.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.
