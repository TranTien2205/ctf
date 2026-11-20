# Trap: Unsorted JSONL fakes a gap

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Sorting EventRecordID over an unordered export manufactures gaps. Sort by identifier first, then check contiguity — same lesson as evtx-dump-order.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
