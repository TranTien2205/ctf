# Timestomp: Copy/move timestamp semantics

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A copied file gets fresh times in BOTH sets — not tampering, just copy semantics; a MOVE preserves times. Distinguish before accusing: divergence, not 'old times', is the test.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
