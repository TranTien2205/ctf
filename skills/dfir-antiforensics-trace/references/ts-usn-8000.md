# Timestomp: $J reason 0x8000 BASIC_INFO_CHANGE

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Microsoft's definition: 'a user has either changed one or more file or directory attributes (for example, the read-only, hidden, system, archive, or sparse attribute), or one or more time stamps' (USN_RECORD_V2). So 0x8000 ALONE is not backdating — a `+H +S` attrib sets the same bit. Pair it with the $FN divergence or a Sysmon 2 before claiming timestomp.

## Evidence rule

The divergence (or the Previous/Creation pair) is the quotable record —
never a single suspicious-looking timestamp.

## Pivot

No Sysmon 2, no $MFT in bundle -> the prefetch/Amcache time columns as
weaker corroboration (`rec-*` modules).
