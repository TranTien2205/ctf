# Scenario: Worked HTTP-upload case sketch

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

conv,tcp shows upload-heavy flow to one peer -> http_req,tree names the URI + POST count -> `--export-objects http` recovers bodies -> file type/hash answers 'what'. UA clustering (`q-ua-anomaly`) corroborates tool vs browser.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
