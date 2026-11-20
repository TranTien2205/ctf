# Negative: Run family clean

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

HKLM Run/RunOnce/RunOnceEx/Policies + Wow6432Node + every NTUSER equivalent checked; Winlogon Shell/Userinit at defaults  -  the registry autostart family is closed.

## Pivot

Closing module -> the sweep order or the next family.

## Cross-check

The module is one line in the sweep; the claim it feeds still needs
the verbatim record and the paired timestamps before it counts.
