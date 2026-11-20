# Scenario: Events that should exist but don't

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A login/process that left no record: check 4719 (audit policy cleared), Sysmon 4/16 (Sysmon disabled/reconfigured), 1100 (logging stopped) — the SILENCE is the tamper record; the content is unrecoverable except through survivors.

## Evidence rule

The scenario names the record chain; every link still needs its verbatim
quote through post-probe.

## Pivot

Chain breaks -> the rec-* column for whatever was destroyed.
