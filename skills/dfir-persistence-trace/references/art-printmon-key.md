# Module: Artifact: Print monitor key

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

SYSTEM `<set>\Control\Print\Monitors\<name>` `Driver` = DLL  -  spoolsv loads at boot as SYSTEM; stock monitors are a known list; a foreign monitor name + Driver path is the record.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
