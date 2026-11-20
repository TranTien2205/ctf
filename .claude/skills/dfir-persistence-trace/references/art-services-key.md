# Module: Artifact: Services key anatomy

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

SYSTEM `<set>\Services\<name>`: required `ImagePath`, `Type`, `Start`, `ObjectName`; optional `DisplayName`, `Description`, `FailureActions`, `Parameters\ServiceDll`, `Security\Security` SDDL. Enum subkeys of Services for the full installed list  -  compare Start 0-2 only for reboot persistence.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
