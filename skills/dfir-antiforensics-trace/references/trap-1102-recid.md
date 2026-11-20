# Trap: 1102 EventRecordID is not always 1

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Usually 1, but Microsoft's own documented sample XML carries <EventRecordID>1087729</EventRecordID>. Read and quote the value; never assert the usually.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
