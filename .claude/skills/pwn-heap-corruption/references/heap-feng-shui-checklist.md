# Heap feng shui — grooming the layout — checklist

Companion to `heap-feng-shui.md`.

## Checklist

- [ ] Script the alloc/free sequence; never click through it interactively.
- [ ] Fill tcache first (7 frees per size) so later frees hit fastbin/
- [ ] Allocate a guard chunk before an overflow target so the overflow
- [ ] Spray decoy chunks to shape adjacency before a coalescing move.
