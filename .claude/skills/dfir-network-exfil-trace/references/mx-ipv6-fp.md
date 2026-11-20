# ipv6 — Classic false positive

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## For the `ipv6` channel

happy-eyeballs parallel v6 for legit v4 traffic.

## Cross-references

- channel module: `chan-ipv6.md` (detection stack)
- direction trap: `trap-direction.md`
- claim vs observation: `meth-claim-vs-obs.md`

## Evidence rule

Quote the filter result or the tap row that produced the number/name. `->`/Tx/toserver = outbound; check direction before reporting.

## Pivot

This cell dry -> the sibling cells for `ipv6`; the channel itself absent -> `chan-*` inventory and the class falsifier.
