# Module: Artifact: Tasks dir layout

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`C:\Windows\System32\Tasks\` mirrors the scheduler folder tree  -  file name = task name, no extension, UTF-16-le XML. Microsoft\Windows\* subtrees are stock; anything at root or in a foreign folder is the anomaly.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
