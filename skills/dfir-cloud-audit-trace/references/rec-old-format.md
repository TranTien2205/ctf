# Recovery: old file formats

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Pre-2021 flow logs (10 fields) and earlier CloudTrail schemas - check field COUNT before field position; the 14-field positions only hold on the default format.

## Rule

A recovery module names the fallback artifact when the primary store
is gone or degraded - the fallback record is still quoted verbatim.

## Pivot

Recovery exhausted -> `../dfir-antiforensics-trace/` for the
destroyed-artifact matrix.
