# Heap vs stack corruption — why the recipes differ


Stack corruption is linear (overflow → ret-addr); heap corruption is
relational (the bug changes allocator state, the allocator's own
mechanics deliver the write). The difference changes everything.

## Implications

- No single "return address" target — the targets are bin pointers,
  size fields, hooks and FILEs.
- The write often happens on a LATER alloc/free — not on the corrupting
  op.
- Order matters more than bytes: the alloc/free sequence IS the
  payload.
- Detection is indirect: crashes on malloc/free, wrong-size returns,
  allocator aborts — not a RIP overwrite.

## Falsifier

The bug is a pure linear overflow with no allocator-state reach: it's
pwn-stack-overflow, not this class.
