# Scenario: Bundle is only a pcap

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

1) `capinfos -a -e -c -z` — window, count, size; quote it. 2) `tshark -q -z io,phs -z endpoints,ip` — protocol mix + per-host Tx/Rx. 3) `conv,tcp`+`conv,udp` — rank peers by `->` (SECOND pair). 4) channel taps for whatever `io,phs` showed. 5) `pcap_triage.py --input cap --challenge <n>` as the stdlib cross-check. Every number reported comes with its row; 'no dominant peer + nothing above tcp/udp/tls' is the falsifier path.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
