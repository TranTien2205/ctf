# Consolidation — when the heap merges chunks


The allocator merges adjacent free chunks on certain events: free() of
a fastbin-adjacent gap, a large malloc that scans bins, malloc_consolidate
itself — the merge is what makes overlap attacks work.

## Triggers

- free() of a chunk adjacent to the top or another free chunk.
- malloc_consolidate() — called on large requests or explicitly.
- An unsorted-bin pass merging neighbors.

## Why it matters

- The merge walks prev_size backward when P is clear — an off-by-NUL
  that clears P makes the merge eat a live chunk.
- Coalesced size = sum of merged chunks — one big free chunk covering
  live data.

## Falsifier

The merge never runs (all frees land in tcache/fastbin where no
consolidation happens): consolidate-based overlaps need a bin the merge
actually touches — exhaust tcache first.
