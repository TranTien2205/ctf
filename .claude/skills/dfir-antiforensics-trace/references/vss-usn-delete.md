# Journal/shadow: fsutil usn deletejournal

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`fsutil usn deletejournal /d c:` disables the journal and returns I/O control while it drains; `/n` returns only after. Microsoft's remark: disabling 'must access all the records in the master file table (MFT) and set the last USN attribute to 0 (zero)' — a volume whose MFT records ALL carry USN 0 was journal-deleted rather than merely wrapped.

## Evidence rule

A destroyed-journal claim needs BOTH records: the delete evidence (command
line or USN-0 pattern) AND the survivor actually checked for what it holds.

## Pivot

Shadow/journal routes exhausted -> the rec-* recovery table picks the next
column; toolchain gaps route through `skills/dfir-sherlock-triage/toolchain.md`.
