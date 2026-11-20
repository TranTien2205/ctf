# Deletion: SDelete fingerprints

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Three: (1) `HKU\<SID>\SOFTWARE\Sysinternals\SDelete\EulaAccepted`=1 — proof it ran under that SID, last-written time dates it; (2) the 26-rename burst in $J: 'renames the file 26 times, each time replacing each character ... first rename of foo.txt would be to AAA.AAA' (Microsoft Learn, SDelete) — 26 rename pairs (0x1000+0x2000) on ONE FileReferenceNumber = one wiped file; (3) `sdelete -c` fills free MFT with records that 'fit within an MFT record' — an $MFT full of tiny equal-sized records is the free-space wipe.

## Evidence rule

Deletion evidence is a record pair: the delete event/journal row AND the
surviving artifact that proves it was deleted, not merely absent. A missing
file alone is never the record.

## Pivot

Deletion records cleaned too -> the recovery-order table (`rec-*`) picks the
next surviving family.
