# The leak ladder — what leaks feed what — checklist

Companion to `the-leak-ladder.md`.

## Checklist

- [ ] Code pointer → binary base (PIE).
- [ ] GOT contents → libc base.
- [ ] Stack pointer (saved rbp/env) → ret-addr slots / pivot targets.
- [ ] Heap pointer → heap-anchored fakes.
