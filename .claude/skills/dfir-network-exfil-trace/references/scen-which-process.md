# Scenario: The 'which process sent it' question

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

pcap alone CANNOT answer it — hand to host side: Sysmon 3 `ProcessGuid` -> Sysmon 1 gives Image+CommandLine; 5156 gives the device-path `Application`; SRUM `AppId` gives the app label (via map table). If the bundle has no host telemetry, the honest answer is 'unattributable from this bundle' with the flow evidence quoted.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
