# The null-byte boundary — off-by-null precisely — checklist

Companion to `the-null-trick.md`.

## Checklist

- [ ] 1. Size shrinks: the chunk's end moves back — later metadata sits
- [ ] 2. P clears: prev_size activates — consolidation can walk backward.
- [ ] The shrunken size must still be sane (>= MINSIZE, aligned).
- [ ] prev_size must be forgeable for the backward walk.
