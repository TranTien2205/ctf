# The bins — tcache, fastbin, unsorted, small, large


Freed chunks are sorted into bins by size and freeness; the bin decides
what the chunk gives you.

## The four bins that matter

- tcache: per-thread, 64 entries, sizes <= 0x410 (default), LIFO.
  First destination of frees (glibc >= 2.26).
- fastbin: small chunks <= 0x80-ish, singly-linked, no consolidation.
- unsorted: the staging bin — first free of a larger chunk; fd/bk point
  at the bin header → the libc leak.
- small/large: size-sorted doubly-linked lists for medium/large chunks.

## What each buys

- tcache poisoning → fastest arbitrary-write path (pre-2.32 without
  safe-linking; post-2.32 needs a leak).
- fastbin dup → classic overlapping chunk.
- unsorted leak → libc base.
- largebin → the house-of-… write chains.

## Falsifier

The chunk size never reaches the bin you need (too small for unsorted,
too big for tcache): the technique must fit the allocation sizes the
program allows.
