# Consolidation — when the heap merges chunks — checklist

Companion to `malloc-consolidate.md`.

## Checklist

- [ ] free() of a chunk adjacent to the top or another free chunk.
- [ ] malloc_consolidate() — called on large requests or explicitly.
- [ ] An unsorted-bin pass merging neighbors.
- [ ] The merge walks prev_size backward when P is clear — an off-by-NUL
- [ ] Coalesced size = sum of merged chunks — one big free chunk covering
