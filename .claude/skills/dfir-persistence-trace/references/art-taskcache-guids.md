# Module: Artifact: TaskCache GUID joins

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Tree\<path> -> Id = GUID -> Tasks\{GUID} -> Path/Actions/Triggers/DynamicInfo/SecurityDescriptor. The join survives XML deletion because it lives in the hive; a GUID with no Tree entry is the orphan shape.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
