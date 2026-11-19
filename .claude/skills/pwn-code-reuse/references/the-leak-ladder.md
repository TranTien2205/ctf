# The leak ladder — what leaks feed what


- Code pointer → binary base (PIE).
- GOT contents → libc base.
- Stack pointer (saved rbp/env) → ret-addr slots / pivot targets.
- Heap pointer → heap-anchored fakes.

The order is usually: code/libc first (the chain's addresses), stack
second (if a stack target is needed).
