# Module: Field table: Sysmon 19-21

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

19 WmiEventFilter (Operation, Name, Query), 20 WmiEventConsumer (Name, Type, Destination=the commandline/script), 21 WmiEventConsumerToFilter (Consumer path + Filter path  -  the binding pair).

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
