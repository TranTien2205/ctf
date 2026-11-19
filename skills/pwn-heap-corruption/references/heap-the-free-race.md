# The free race — ordering the corruption


Between the free() and the corruption-write there's a window where the
chunk's bin links are live: write during the window or the stale data
isn't the link.

## The timing

- free() writes fd/key into the chunk — YOUR write must come after.
- A second alloc returns the chunk — your stale write is overwritten.

## Falsifier

The window is closed by the op ordering: the corruption can't land in
time.
