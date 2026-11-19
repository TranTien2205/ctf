# Sparse layouts — non-contiguous heaps


Not all heaps are contiguous: fresh allocs, madvise gaps, and mmap'd
regions can sit between chunks — adjacency assumptions fail.

## Check

dm maps the real regions; don't assume chunk A's neighbor is chunk B.

## Falsifier

The layout isn't contiguous — grooming must work with the real map.
