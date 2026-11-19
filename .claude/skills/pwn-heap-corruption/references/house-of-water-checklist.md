# House of water — tcache-perthread header forgery — checklist

Companion to `house-of-water.md`.

## Checklist

- [ ] 1. The struct sits at heap_base+0x10 — the heap's first chunk.
- [ ] 2. Arbitrary write into counts[] (64 bytes) + entries[] (64 pointers).
- [ ] 3. Set count[i]=1, entries[i]=target — the next size-i alloc returns
- [ ] No LIFO walk needed — the entry IS the return.
- [ ] Works post-safe-linking if you already have a write.
