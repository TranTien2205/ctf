# Trap: Absent artifact != tampering

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A fresh NTFS volume has no $J at all — `dfir-filesystem-timeline` measured it: the journal is created on first use. Absence is creation scope or collection scope first; tampering needs its own positive record.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
