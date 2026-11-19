# House of mind — arena redirection


Corrupt a chunk's N (non-main-arena) bit plus arena reference so free()
deposits it into a DIFFERENT arena — a fake arena planted in controlled
memory gives bin control.

## Steps (classic form)

1. Set the victim chunk's N bit (size | 4).
2. Compute heap_info_for from the chunk address → point it at a fake
   heap_info + arena you control.
3. free() routes the chunk into your fake arena's bins.
4. Allocations from that arena return your planted chunks.

## Limits

- Needs substantial fake-structure setup in writable memory.
- The arena arithmetic is version-sensitive.

## Falsifier

Can't control a heap_info-shaped region the allocator will trust:
house-of-mind unreachable.
