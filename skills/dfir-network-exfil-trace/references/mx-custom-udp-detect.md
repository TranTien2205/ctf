# custom-udp — Detection shape

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## For the `custom-udp` channel

io,phs `data` under udp + single-peer concentration.

## Cross-references

- channel module: `chan-custom-udp.md` (detection stack)
- direction trap: `trap-direction.md`
- claim vs observation: `meth-claim-vs-obs.md`

## Evidence rule

Quote the filter result or the tap row that produced the number/name. `->`/Tx/toserver = outbound; check direction before reporting.

## Pivot

This cell dry -> the sibling cells for `custom-udp`; the channel itself absent -> `chan-*` inventory and the class falsifier.
