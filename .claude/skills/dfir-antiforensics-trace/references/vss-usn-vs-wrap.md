# Journal/shadow: Journal deleted vs journal wrapped

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

USN 0 on all MFT records = deleted journal; a journal that wrapped naturally keeps current USNs with a high LowUsn boundary. The distinction is the $MFT-wide read, not the journal file itself.

## Evidence rule

A destroyed-journal claim needs BOTH records: the delete evidence (command
line or USN-0 pattern) AND the survivor actually checked for what it holds.

## Pivot

Shadow/journal routes exhausted -> the rec-* recovery table picks the next
column; toolchain gaps route through `skills/dfir-sherlock-triage/toolchain.md`.
