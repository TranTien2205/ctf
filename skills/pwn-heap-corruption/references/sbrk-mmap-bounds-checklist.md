# The heap bounds — brk vs mmap — checklist

Companion to `sbrk-mmap-bounds.md`.

## Checklist

- [ ] brk heap: contiguous region — adjacency grooming works.
- [ ] mmap'd chunks: isolated pages — no heap neighbors to corrupt.
- [ ] The gap between regions: not allocatable.
