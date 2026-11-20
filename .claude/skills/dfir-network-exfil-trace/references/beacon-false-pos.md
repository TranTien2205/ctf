# Beacon: Beacon lookalikes

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Keepalives, NTP sync, telemetry heartbeats, WS pings, ARP — all periodic. A beacon answer needs the peer to also be suspicious (external, low-entropy domain, new-first-seen), not merely periodic.

## Evidence rule

A cadence claim needs the numbers: n, median, mad, cv — or the quoted
io,stat series. 'Looked regular' is not measurable and not recordable.

## Pivot

cv low AND peer suspicious -> `q-periodic-beacon`; cv high -> drop the
beacon hypothesis for this peer and record the negative.
