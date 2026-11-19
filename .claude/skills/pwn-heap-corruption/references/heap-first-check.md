# The very first check — does the class apply?


Before anything: does input reach allocator state at all?

## The test

- A read/write op on an allocated object → yes, the surface exists.
- A free that leaves a dangling ref → UAF open.
- An overflow reaching the next chunk's header → metadata corruption
  open.
- A double-free path → dup open.

## Falsifier

No path from input to allocator state: closed — the bug is elsewhere.
