# Trap: evtx_dump emits out of order

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Multithreaded by default — a 'gap' read off an unsorted dump is an artefact of the dump. Pass `-t 1` for ordered output before any gap arithmetic. (Absent here; the rule transfers to any multi-worker converter.)

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
