# Trap: Prefetch proves payload, not mechanism

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

A .pf for the payload proves the payload ran. The mechanism is proven by the PARENT (taskeng/svchost -k/services/explorer/wmiprvse)  -  read the parentage off Sysmon 1 or Operational 129.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
