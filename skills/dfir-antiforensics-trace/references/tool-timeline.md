# Tool: tools/forensics/timeline_merge.py

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`--source PATH:TIMECOL:LABEL` per artifact — puts a clear event, a gap bound, and the survivor records on one axis so the hole's dates are computed, not estimated.

## Verification

`--help`/`--selftest` before relying on flags. No tool in this list was
assumed; absent tools are routed to `skills/dfir-sherlock-triage/toolchain.md`.
