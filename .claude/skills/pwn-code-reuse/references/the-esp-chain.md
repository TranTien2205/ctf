# The esp-chain — x86 layout


x86: the same idea with 4-byte slots — [func][ret][arg0][arg1] — the
stack is the program.

## The difference

- Args are stack entries, not pops.
- A pop gadget sets a register for a different use (an index, a
  pointer), not a call arg.
