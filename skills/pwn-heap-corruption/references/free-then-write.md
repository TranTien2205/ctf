# Free then write — the order matters


Writing a chunk BEFORE freeing leaves data; writing AFTER freeing
corrupts bin state — the same write, different primitive.

## The order

- write then free: the bytes you wrote are just data (they get
  overwritten by fd/bk on the free anyway).
- free then write: your bytes land on fd/key — the poison.

## The classic bug

A UAF where the write comes after free — the bin fields are live: the
write IS a bin corruption.

## Falsifier

The program's order is fixed write-then-free (no post-free write path):
the corruption channel isn't there.
