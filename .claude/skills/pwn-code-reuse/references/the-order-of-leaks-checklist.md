# The order of leaks — which first — checklist

Companion to `the-order-of-leaks.md`.

## Checklist

- [ ] 1. Code/binary base (PIE) — the chain's addresses need it.
- [ ] 2. libc base — the libc functions/offsets need it.
- [ ] 3. Stack — only if a stack target is aimed.
- [ ] 4. Heap — only for heap-anchored fakes.
