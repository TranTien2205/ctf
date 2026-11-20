# Scenario: Bundle is only event logs

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

No capture: volume comes from host counters. 1) `evtx_query.py --input sysmon.jsonl --event-id 3 --field-contains DestinationIp=. --challenge <n>` — per-connection process+destination. 2) Sysmon 22 for DNS-side names. 3) Security 5156 for WFP-level flow allows (numeric Protocol, device-path Application). 4) DNS-Client 3006/3008 for resolution detail. Bytes are not counted by these events — answer 'who talked to what', and say plainly that byte volume is unmeasurable from this bundle unless SRUM or a firewall log is present.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
