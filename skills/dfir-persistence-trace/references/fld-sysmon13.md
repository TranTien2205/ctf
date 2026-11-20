# Module: Field table: Sysmon 13 registry set

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

EventType SetValue, TargetObject (full key+value path), Details (the new data)  -  the per-value timestamp the hive's one-timestamp key cannot give; the definitive 'when was this Run value written' answer.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
