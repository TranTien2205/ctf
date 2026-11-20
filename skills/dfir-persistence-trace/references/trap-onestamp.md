# Trap: One timestamp per key

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Key lastChange dates the newest write to ANY value under it  -  a Run key's timestamp does not date the value you are quoting. Sysmon 13 or $J is needed for per-value timing.

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
