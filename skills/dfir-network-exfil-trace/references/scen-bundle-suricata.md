# Scenario: Bundle with eve.json

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`jq` by `event_type`: `flow` rows carry `bytes_toserver/toclient` (rank those), `alert` rows carry signature+`flow_id` (pivot, not volume), `fileinfo` carries stored files, `stats` carries drop counts that qualify everything. `toserver` direction follows src_ip->dest_ip — verify initiator before claiming outbound.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
