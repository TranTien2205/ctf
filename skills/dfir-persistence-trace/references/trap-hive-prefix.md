# Trap: Doubled hive prefix looks like absence

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`-name 'HKLM\SOFTWARE\...'` on a SOFTWARE hive returns key-not-found  -  the root IS the mount point. A 'no Run key' finding after a doubled-prefix query is a tool error, not a record.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
