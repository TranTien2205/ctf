# Which bin — the routing table — checklist

Companion to `bin-map.md`.

## Checklist

- [ ] size <= 0x410 (x64), tcache[i] not full → tcache.
- [ ] size <= fastbin max (~0x80), tcache full → fastbin.
- [ ] else → unsorted (one pass) → small/large on next alloc sweep.
- [ ] exact tcache match first, then fastbin (small sizes), then unsorted
