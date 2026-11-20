# Deep dive: Deep: orphaned vs armed WMI

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

An `__EventConsumer` without a binding is inert  -  the payload text can be quoted but the persistence claim needs the binding object (5861 / Sysmon 21 / the strings hit on FilterToConsumer). Report an orphan as debris, not live persistence.

## Use

Depth for when the row-level module is not enough  -  cite this file's
artifact and offset when the claim rests on the decoded detail.

## Pivot

Deep read done -> back to the scenario (`scen-*`) or the matrix.
