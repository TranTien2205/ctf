# Method: Reading SecurityDescriptor SDDL

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

TaskCache `Tasks\{GUID}` `SecurityDescriptor` is SDDL  -  the O: owner SID and the ACEs name who can write the task. The SDDL survives XML deletion, so it is the creator-attribution fallback. Resolve SIDs via the SAM hive or the known SID table.

## Discipline

One mechanism family per probe. Three reads of one family with no new
record -> pivot per the budget rule.

## Pivot

Method exhausted -> `scen-*` scenario for the bundle shape.
