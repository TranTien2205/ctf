# Scenario: The 'how much data' question

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Decide wire vs payload FIRST: `endpoints,ip` Tx Bytes = wire; `tcp.len`/`udp.length-8` sums = near-payload; Zeek `orig_bytes` = payload; SRUM `BytesSent` = app-level. State which the question means; when ambiguous report the payload figure and note the wire bound.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
