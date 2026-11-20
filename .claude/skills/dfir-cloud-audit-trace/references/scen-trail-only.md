# Scenario: Scenario: CloudTrail bundle only

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Route: inventory -> decompress+TSV -> group by accessKeyId -> recon-then-act boundary -> the question's field -> window bounds on eventTime. No host, no flows - absence claims stay inside what the trail can record.

## Exit

Ends with a quoted record + window bounds, or a recorded negative and
the next family named.

## Pivot

Done -> `work-*` for reporting discipline.
