# Trap: Dormant ControlSet is history

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Values in ControlSet002 when Select\Current=1 are a PREVIOUS config  -  LastKnownGood or an old boot. Answer the live set; cite the dormant set only as history.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
