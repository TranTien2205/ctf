# Scenario: Scenario: hives only, no logs

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

registry-read.py over SOFTWARE/SYSTEM/NTUSER.DAT + TaskCache  -  the DynamicInfo struct unpack carries the 'when did it run' question alone. Timing from key lastChange only, with the one-timestamp trap attached.

## Exit condition

Each scenario ends with either a verbatim record quoted, or a recorded
negative and the next family named.

## Pivot

Scenario done -> `work-*` for the reporting discipline.
