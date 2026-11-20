# Scenario: The binary 'was there exfiltration' question

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Refuse the bare yes/no — answer with the measured shape: 'N bytes to external peer P over channel C during window W' IS the answer form. A clean negative is the quoted falsifier block, not the word 'no'.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
