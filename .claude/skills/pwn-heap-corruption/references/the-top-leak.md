# Reading the top — the heap's end pointer


main_arena.top points at the wilderness — a heap address leaked through
a dangling unsorted chunk's neighbors or a direct arena read.

## Why it matters

- top's value = heap_base + heap_size → names the heap's extent.
- top-adjacent allocs are the wilderness — corruption of top's size is
  house-of-force.

## Falsifier

Nothing leaks an arena member and no unsorted access exists: top stays
unknown — not usually needed anyway.
