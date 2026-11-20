# Module: Artifact: W32Time providers

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

SYSTEM `<set>\Services\W32Time\TimeProviders\<name>`: DllName + Enabled=1 + InputProvider flag  -  loaded by the w32time service as LOCAL SERVICE; a foreign provider fires with the time service.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
