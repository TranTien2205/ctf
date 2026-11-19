# tcache_perthread_struct — the per-thread control — checklist

Companion to `the-tcache-struct.md`.

## Checklist

- [ ] counts[i]=N fabricates bin occupancy.
- [ ] entries[i]=P aims the next size-i alloc at P.
- [ ] A single contiguous write of ~0x240 bytes controls the whole tcache.
