# Recovery: Destroyed: Defender history (1013)

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns: quarantine `Entries` (detections still listed), MPLog `DETECTION_ADD` lines, 1116/1117 events (if the channel survived), 1120 `Hashes` (when ThreatFileHashLogging was set).

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.
