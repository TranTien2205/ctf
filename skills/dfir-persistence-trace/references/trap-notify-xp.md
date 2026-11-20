# Trap: Winlogon Notify is XP-era

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Post-Vista winlogon does not load notification packages  -  a Notify value is probably stale or a decoy; verify the OS build before citing it as live persistence (UNVERIFIED prevalence).

## Guard

Check this trap BEFORE the claim it protects  -  the failure is silent:
the wrong answer reads as plausible as the right one.

## Pivot

Traps clear -> continue the mechanism sweep (`meth-order`).
