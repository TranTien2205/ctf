# Scenario: Mixed capture + logs bundle

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Run the pcap path for volume/direction AND the EVTX path for process attribution — they answer different halves. Join on `timeline_merge.py --source net.csv:frame.time_epoch:net --source sysmon.jsonl:Event.System.TimeCreated.SystemTime:sysmon --gap 600` to put flow and process events on one axis; the process owning the socket at the exfil instant is the attribution answer.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
