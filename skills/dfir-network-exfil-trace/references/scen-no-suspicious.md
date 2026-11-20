# Scenario: Nothing looks suspicious

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The falsifier check, run honestly: `io,phs` clean, no dominant external peer, host counters absent or clean. Then the question is usually 'where else could it hide': timing channels (`chan-timing`), legitimate services (`chan-cdn-abuse`), IPv6 (`chan-ipv6`), or the capture itself is truncated (`meth-truncated`). Three families empty = record and pivot per Discipline.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
