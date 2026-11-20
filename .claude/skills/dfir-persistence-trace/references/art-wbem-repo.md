# Module: Artifact: wbem repository layout

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`C:\Windows\System32\wbem\Repository\` holds OBJECTS.DATA, INDEX.BTR, MAPPING*.MAP (and sometimes MAPPING1/2/3 generations). The namespace structure inside OBJECTS.DATA is what the consumer objects live in  -  root\subscription is where permanent subscriptions register; a subscription created under another namespace still fires.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
