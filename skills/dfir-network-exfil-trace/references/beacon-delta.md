# Beacon: Inter-packet delta arithmetic

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Per-flow deltas: sort `frame.time_epoch` within `tcp.stream`/peer key, diff successive timestamps. Median = the period; MAD = the jitter figure; CV = the classifier. Measured: beacon n=39 median=30.14 mad=1.36 cv=0.054 vs browsing n=11 median=395.21 mad=104.64 cv=0.546 — an order of magnitude separates them on cv.

## Evidence rule

A cadence claim needs the numbers: n, median, mad, cv — or the quoted
io,stat series. 'Looked regular' is not measurable and not recordable.

## Pivot

cv low AND peer suspicious -> `q-periodic-beacon`; cv high -> drop the
beacon hypothesis for this peer and record the negative.
