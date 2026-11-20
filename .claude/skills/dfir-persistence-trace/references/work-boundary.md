# Class boundary

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

This class answers *what re-fires without the attacker*. It does not
answer: who logged on (`dfir-authentication-trace`), what ran once
(`dfir-execution-trace`), how the record was destroyed
(`dfir-antiforensics-trace`), what left the network
(`dfir-network-exfil-trace`), or what the disk's own timestamps say
(`dfir-filesystem-timeline`). Each cross module names its sibling.

## Pivot

Boundary applies -> route, do not stretch the claim.

## Cross-check

The module is one line in the sweep; the claim it feeds still needs
the verbatim record and the paired timestamps before it counts.
