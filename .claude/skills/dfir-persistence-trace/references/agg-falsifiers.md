# Aggregator: Falsifier index

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

The class falsifier is an AND: no 7045 + no 4697 + no foreign Tasks XML + four Run keys + Winlogon Shell/Userinit default + OBJECTS.DATA strings clean + startup/Office/BITS clean -> close and route out. Per-family falsifiers live in each `*-route` card.

## Use

An index  -  open the named family module for the artifact detail; this
file only decides which one.

## Pivot

Index consulted -> the module it names.
