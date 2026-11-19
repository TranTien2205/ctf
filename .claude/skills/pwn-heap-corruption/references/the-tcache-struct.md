# tcache_perthread_struct — the per-thread control


The heap's first bytes (heap_base+0x10): counts[64] then entries[64] —
the per-thread tcache state.

## Layout (x64)

    counts:   64 bytes (one per size class)
    entries:  64 pointers (bin heads)

## Why it's a target

- counts[i]=N fabricates bin occupancy.
- entries[i]=P aims the next size-i alloc at P.
- A single contiguous write of ~0x240 bytes controls the whole tcache.

## Falsifier

No write reaches the heap's start: the struct stays honest — use
per-chunk corruption instead.
