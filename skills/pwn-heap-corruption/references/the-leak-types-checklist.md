# The three leaks — heap, libc, stack — checklist

Companion to `the-leak-types.md`.

## Checklist

- [ ] Heap leak: a chunk's own address — needed for safe-linking aims and
- [ ] Libc leak: unsorted fd/bk → main_arena → base. Sources: the first
- [ ] Stack leak: environ (libc offset) or a saved rbp/argv pointer in a
