# The three states — alloc/free/dangling


Every slot is in one of three states: allocated (live), freed (in a
bin), dangling (freed but referenced) — the table tracks all three.

## The confusion

The bug is a state confusion: the program thinks dangling is
allocated, or the allocator thinks allocated is free — the exploit
lives in the gap.

## Falsifier

The program's bookkeeping matches the allocator's exactly: no gap.
