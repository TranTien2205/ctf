# Recovery: mixed timezones

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

eventTime is always UTC; S3 Time carries %z; host logs may be local - normalise EVERYTHING to UTC before merge (answer-discipline.md).

## Rule

A recovery module names the fallback artifact when the primary store
is gone or degraded - the fallback record is still quoted verbatim.

## Pivot

Recovery exhausted -> `../dfir-antiforensics-trace/` for the
destroyed-artifact matrix.
