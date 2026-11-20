# Scenario: A channel that is empty or stub

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Header-only .evtx = truncated/carved — NOT cleared. Distinguish: cleared files still hold record id 1 (often the 1102 itself); stubs hold zero chunks. The `if not ids` guard keeps the loop alive past the stub — measured on the fixtures.

## Evidence rule

The scenario names the record chain; every link still needs its verbatim
quote through post-probe.

## Pivot

Chain breaks -> the rec-* column for whatever was destroyed.
