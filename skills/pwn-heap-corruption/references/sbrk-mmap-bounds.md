# The heap bounds — brk vs mmap


The main heap grows via brk (contiguous after the binary or mmap'd for
PIE); big/huge allocations mmap separately — the boundary shapes what
overflows can reach.

## The geography

- brk heap: contiguous region — adjacency grooming works.
- mmap'd chunks: isolated pages — no heap neighbors to corrupt.
- The gap between regions: not allocatable.

## Falsifier

The target object sits in an isolated mmap region: no heap technique
reaches it.
