# Leak before write — the order that survives versions — checklist

Companion to `leak-before-write.md`.

## Checklist

- [ ] 1. Unsorted-bin fd/bk → libc base (the free leak).
- [ ] 2. Heap fd de-mangle → heap base (safe-linking requires it).
- [ ] 3. environ (libc offset) → stack.
- [ ] 4. A leaked code pointer → binary base (PIE).
