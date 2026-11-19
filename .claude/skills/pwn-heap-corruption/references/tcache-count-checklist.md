# tcache counts[] — the per-size tally — checklist

Companion to `tcache-count.md`.

## Checklist

- [ ] 1. tcache struct sits at the heap's start (usually heap_base+0x10).
- [ ] 2. Write count[i] = N for a size i — the bin now believes it holds N
- [ ] 3. The next alloc of size i follows the (corrupted or stale) entry
- [ ] counts[] is a byte array — a single byte-write suffices.
- [ ] Combined with entry corruption, it's arbitrary allocs.
