# Scenario: When the answer IS the flag

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Some challenges make the reassembled payload literally the flag string (DNS chunks decode to `flag{...}` or a file contains it). The flag still goes through `hooks.py pre-flag` — read it from the reassembled bytes (a supplied artifact), never typed from memory.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
