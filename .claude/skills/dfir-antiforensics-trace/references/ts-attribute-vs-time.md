# Timestomp: Attribute change vs timestamp change

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The 0x8000 ambiguity resolved: check whether $SI MAC times changed while $FN stayed put (timestomp) vs only flags toggled (attrib). `fsutil usn` record detail and the MFT row decide; the reason bit alone cannot.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
