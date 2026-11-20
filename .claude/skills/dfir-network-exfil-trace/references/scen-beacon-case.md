# Scenario: Worked beacon case sketch

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

endpoints shows a peer with modest volume -> io,stat series is flat or pandas cv is ~0.05 -> jitter figure via mad/median -> the peer's other properties (first-seen, domain entropy, port) decide whether 'periodic' also means 'C2' — cadence alone is not suspicious (`beacon-false-pos`).

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
