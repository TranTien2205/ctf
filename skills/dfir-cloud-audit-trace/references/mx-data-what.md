# Matrix: CloudTrail data events - what action

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

For CloudTrail data events, "what action" resolves through eventName/Operation/eventType + the target field.
The record is the Data-category record; the base module is `s3-data-events.md` - read it for the
field names and the traps before quoting.

## Falsifier

If the record named above is absent AND the artifact is confirmed
parsed, the artifact did not produce this answer - record the negative
and move to the next cell or family.
