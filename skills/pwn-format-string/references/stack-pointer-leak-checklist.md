# Leaking a stack pointer — for ret-addr writes — checklist

Companion to `stack-pointer-leak.md`.

## Checklist

- [ ] 1. In the %p dump, find stack-shaped words (0x7ff... on x64 Linux).
- [ ] 2. A saved rbp points to the previous rbp — the saved ret is prev_rbp+8.
- [ ] 3. An argv/env pointer leaks the stack top region.
- [ ] 4. Once a stack addr is known, the ret-addr slot is computable.
