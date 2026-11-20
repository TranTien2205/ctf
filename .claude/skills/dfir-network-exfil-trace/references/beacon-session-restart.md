# Beacon: Reconnect-spawned periodicity

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A process that dials home on a timer and drops makes many SHORT periodic flows — group by peer socket pair OR by `ip.dst` alone when the port cycles, else each connection looks one-shot and the cadence is invisible.

## Evidence rule

A cadence claim needs the numbers: n, median, mad, cv — or the quoted
io,stat series. 'Looked regular' is not measurable and not recordable.

## Pivot

cv low AND peer suspicious -> `q-periodic-beacon`; cv high -> drop the
beacon hypothesis for this peer and record the negative.
