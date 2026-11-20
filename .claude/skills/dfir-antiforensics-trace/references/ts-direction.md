# Timestomp: Backdating vs postdating

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Backdating (older Creation) hides recency; postdating (future timestamps) poisons timeline order. Both show as $SI/$FN divergence; the direction reads off which set is 'wrong' relative to the event history and neighbouring files.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
