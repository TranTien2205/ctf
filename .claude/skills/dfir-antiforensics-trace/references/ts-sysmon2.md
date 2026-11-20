# Timestomp: Sysmon event 2 — FileCreateTime

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Fields: `CreationUtcTime` (the planted value), `PreviousCreationUtcTime` (the REAL creation time), `TargetFilename`, `Image`, `ProcessGuid`. The pair IS the timestomp proof — Previous is what SetFileTime overwrote. Microsoft's own caveat: 'many processes legitimately change the creation time of a file; it does not necessarily indicate malicious activity' — installers and archivers fire it constantly, so require the $FILE_NAME divergence or additional context.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
