# Trap: InteractiveToken limits the firing

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

A task with `LogonType` InteractiveToken fires only when THAT user logs on  -  'persists across reboot' is wrong for it; it persists across that user's logons. S4U/Password fire independently.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
