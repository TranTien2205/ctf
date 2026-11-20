# Beacon: Reading jitter correctly

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

mad/median is the jitter percentage a question may ask for (measured 4.5%). A jittered beacon keeps cv low; a perfectly-periodic row with cv~0.00 is suspicious in itself — real tools jitter deliberately.

## Evidence rule

A cadence claim needs the numbers: n, median, mad, cv — or the quoted
io,stat series. 'Looked regular' is not measurable and not recordable.

## Pivot

cv low AND peer suspicious -> `q-periodic-beacon`; cv high -> drop the
beacon hypothesis for this peer and record the negative.
