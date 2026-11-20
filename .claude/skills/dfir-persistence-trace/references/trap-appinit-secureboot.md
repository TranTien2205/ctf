# Trap: AppInit inert under Secure Boot

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Microsoft Learn: disabled when Secure Boot is on since Windows 8. The value sits in the hive and never loads  -  cite it as the INTENDED mechanism only with the Secure Boot state attached.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
