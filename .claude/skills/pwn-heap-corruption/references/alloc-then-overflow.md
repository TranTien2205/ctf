# Alloc-then-overflow — the boundary write


The heap overflow: write past the chunk's user area into the next
chunk's size field — the most direct metadata corruption.

## Steps

1. alloc A(size) — alloc B(size) — adjacency.
2. A's write op overruns into B's size field.
3. Forge B's size/flags → the techniques open (off-by-one family,
   force, consolidation).

## The bound

The write's length cap decides how far past A it reaches: one byte →
LSB corruption; many → full metadata.

## Falsifier

The write stops at the chunk boundary (checked length): no metadata
reach — the bug is data-only.
