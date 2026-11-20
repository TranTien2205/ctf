# Recovery: pandas path fails

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

The jq TSV still answers directly - pandas is the convenience, not the gate; grep/awk on the TSV is the stdlib fallback.

## Rule

A recovery module names the fallback artifact when the primary store
is gone or degraded - the fallback record is still quoted verbatim.

## Pivot

Recovery exhausted -> `../dfir-antiforensics-trace/` for the
destroyed-artifact matrix.
