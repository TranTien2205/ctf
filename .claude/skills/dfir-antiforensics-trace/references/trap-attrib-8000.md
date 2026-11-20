# Trap: 0x8000 is not backdating alone

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

BASIC_INFO_CHANGE covers attribute edits too — `attrib +H +S` sets the same bit as a SetFileTime call. The $J reason is a lead; the divergence is the proof.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
