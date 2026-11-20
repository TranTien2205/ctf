# Journal/shadow: $LogFile as USN survivor

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The NTFS `$LogFile` (transaction log) outlives a USN journal deletion — it records metadata ops for the last minutes of activity. A recovery column when the journal is gone: `$LogFile` -> `$MFT` allocation state -> shadow copy -> prefetch, in that order.

## Evidence rule

A destroyed-journal claim needs BOTH records: the delete evidence (command
line or USN-0 pattern) AND the survivor actually checked for what it holds.

## Pivot

Shadow/journal routes exhausted -> the rec-* recovery table picks the next
column; toolchain gaps route through `skills/dfir-sherlock-triage/toolchain.md`.
