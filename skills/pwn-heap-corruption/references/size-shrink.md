# The size-shrink overlap — free bigger, alloc smaller


Free a large chunk, then alloc smaller — the remainder keeps part of
the old buffer alive while the front reuses it: an automatic overlap
with stale content.

## Steps

1. Free chunk of size S (to unsorted, drain tcache first).
2. Alloc size S' < S → the front returns; the remainder stays in the
   bin — its metadata still in "your" old memory.
3. Old pointers into the remainder region read bin fields (leak) or
   get overwritten by bin ops (corruption).

## Use

- Leak: the remainder's fd/bk point at the arena → libc leak inside
  your old buffer.
- Corrupt: write the remainder's fd via a still-live alias.

## Falsifier

Exact-size allocs only (no split) or the remainder is consumed
immediately: no stale region survives.
