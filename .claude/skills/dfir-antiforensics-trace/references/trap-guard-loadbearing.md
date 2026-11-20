# Trap: Header-only files break the loop

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The `if not ids` guard in the first probe is load-bearing: unguarded, the glob dies IndexError on the first 44-byte stub and never reaches the real channels — one truncated file hides every other one. Measured on the fixtures here.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
