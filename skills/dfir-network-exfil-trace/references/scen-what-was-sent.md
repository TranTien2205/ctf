# Scenario: The 'what was sent' question

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Needs CONTENT, not metadata: `--export-objects <proto>` for carried files; `dns_exfil.py` for label-encoded chunks; `follow,tcp,raw` for stream carving; decoded bodies via `misc-encoding-carrier` techniques. If the channel was TLS without keylog, the honest answer is 'content unreachable; volume + destination are'.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
