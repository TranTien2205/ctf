# Scenario: Worked TLS-volume case sketch

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

TLS leaf dominant in io,phs -> ClientHello SNI vs ip.dst check -> `tls.record.length` summed outbound per stream -> 'Y bytes to ip.dst D claiming name N over T seconds' is the complete answer WITHOUT decryption — say the claim/observation split explicitly.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
