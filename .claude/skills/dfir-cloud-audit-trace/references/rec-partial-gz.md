# Recovery: corrupt gzip member

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

A truncated .json.gz decompresses to a partial last record - jq fails at the truncation; salvage the complete records with a tolerant stream parse and record the boundary.

## Rule

A recovery module names the fallback artifact when the primary store
is gone or degraded - the fallback record is still quoted verbatim.

## Pivot

Recovery exhausted -> `../dfir-antiforensics-trace/` for the
destroyed-artifact matrix.
