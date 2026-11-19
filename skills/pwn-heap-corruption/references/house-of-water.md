# House of water — tcache-perthread header forgery


Forge the tcache_perthread_struct entries/counts directly: fake
counts[] and fake entries[] make every tcache alloc return
attacker-chosen memory — a modern technique (2.33+ friendly).

## The shape

1. The struct sits at heap_base+0x10 — the heap's first chunk.
2. Arbitrary write into counts[] (64 bytes) + entries[] (64 pointers).
3. Set count[i]=1, entries[i]=target — the next size-i alloc returns
   target directly.

## Why it beats poisoning

- No LIFO walk needed — the entry IS the return.
- Works post-safe-linking if you already have a write.

## Falsifier

No write reaches the struct's page: the header-forge is unreachable —
use per-chunk fd poison.
