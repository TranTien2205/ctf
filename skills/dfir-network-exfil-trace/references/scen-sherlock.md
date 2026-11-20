# Scenario: Sherlock-style question list

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Numbered investigation questions (HTB Sherlock shape): answer each from ONE artifact row, in order, via `evtx_query.py --answer` or the tshark row — the tool prints the `pre-flag` argv so values are never retyped. Volume questions -> flow taps; name questions -> SNI/hostname fields; process questions -> Sysmon joins. `skills/dfir-sherlock-triage/` routes the question text.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
