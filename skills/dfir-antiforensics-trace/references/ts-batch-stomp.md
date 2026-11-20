# Timestomp: Batch timestomping

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

One tool touching many files leaves the same planted value across records — a $SI cluster of identical odd dates (e.g. all 2020-01-01) is the batch-tomp shape, and it survives even when per-file $FN diverges correctly.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
