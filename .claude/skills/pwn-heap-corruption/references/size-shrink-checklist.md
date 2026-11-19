# The size-shrink overlap — free bigger, alloc smaller — checklist

Companion to `size-shrink.md`.

## Checklist

- [ ] 1. Free chunk of size S (to unsorted, drain tcache first).
- [ ] 2. Alloc size S' < S → the front returns; the remainder stays in the
- [ ] 3. Old pointers into the remainder region read bin fields (leak) or
- [ ] Leak: the remainder's fd/bk point at the arena → libc leak inside
- [ ] Corrupt: write the remainder's fd via a still-live alias.
