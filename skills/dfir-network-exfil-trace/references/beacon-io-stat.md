# Beacon: The no-pandas variant

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`-z io,stat,60,"COUNT(frame)frame and ip.src==H and ip.dst==P"` — flat per-interval counts are the periodicity signature; `SUM(frame.len)...` adds the volume-per-interval version. Quote the series and the interval width.

## Evidence rule

A cadence claim needs the numbers: n, median, mad, cv — or the quoted
io,stat series. 'Looked regular' is not measurable and not recordable.

## Pivot

cv low AND peer suspicious -> `q-periodic-beacon`; cv high -> drop the
beacon hypothesis for this peer and record the negative.
