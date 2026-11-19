# The bins — tcache, fastbin, unsorted, small, large — checklist

Companion to `the-bins.md`.

## Checklist

- [ ] tcache: per-thread, 64 entries, sizes <= 0x410 (default), LIFO.
- [ ] fastbin: small chunks <= 0x80-ish, singly-linked, no consolidation.
- [ ] unsorted: the staging bin — first free of a larger chunk; fd/bk point
- [ ] small/large: size-sorted doubly-linked lists for medium/large chunks.
- [ ] tcache poisoning → fastest arbitrary-write path (pre-2.32 without
- [ ] fastbin dup → classic overlapping chunk.
- [ ] unsorted leak → libc base.
- [ ] largebin → the house-of-… write chains.
