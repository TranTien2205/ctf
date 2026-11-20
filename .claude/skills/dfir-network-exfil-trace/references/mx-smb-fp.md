# smb — Classic false positive

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## For the `smb` channel

LAN file shares (check peer scope).

## Cross-references

- channel module: `chan-smb.md` (detection stack)
- direction trap: `trap-direction.md`
- claim vs observation: `meth-claim-vs-obs.md`

## Evidence rule

Quote the filter result or the tap row that produced the number/name. `->`/Tx/toserver = outbound; check direction before reporting.

## Pivot

This cell dry -> the sibling cells for `smb`; the channel itself absent -> `chan-*` inventory and the class falsifier.
