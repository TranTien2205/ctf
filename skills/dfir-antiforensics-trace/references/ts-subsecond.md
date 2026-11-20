# Timestomp: The sub-second tell

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`SetFileTime` takes FILETIME in 100ns ticks; a value built from a formatted date string lands on an exact second. Four $SI stamps ending `.0000000` beside a $FN set carrying seven nonzero digits is a planted time. UNVERIFIED here — no real $MFT has been parsed in this tree; treat as a supporting tell only.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
