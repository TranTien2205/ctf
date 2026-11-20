# Timestomp: UTC vs local in the reading

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

All MFT/EVTX times are UTC; displays convert. A 'planted' timestamp reading wrong by exactly the TZ offset is a conversion bug, not tampering — confirm the raw ticks first.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
