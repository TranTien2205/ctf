# Module: Artifact: Netsh helper key

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

SOFTWARE `Microsoft\Netsh`: each value = alias name -> helper DLL path. Loaded on ANY netsh invocation  -  ambient persistence; enum the whole key, the value data is the record.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
