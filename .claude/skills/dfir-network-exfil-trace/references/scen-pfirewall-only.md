# Scenario: pfirewall.log only

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Parse `#Fields:` line, filter `action=ALLOW` (or per the bundle's convention), sum `size` by `dst-ip`. Rotation caveat: if the file starts mid-line, early entries were deleted — the sum is a floor.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
