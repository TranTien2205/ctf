# Size-field corruption — forging chunk boundaries — checklist

Companion to `heap-metadata-corrupt.md`.

## Checklist

- [ ] Enlarged: the chunk's "end" moves into the neighbor — a free absorbs
- [ ] Shrunken: free() puts a partial chunk in a bin; the remainder is a
- [ ] Flag bits: clearing P makes prev_size live — consolidation walks
- [ ] 1. Overflow into the next chunk's size field.
- [ ] 2. Choose the new size so the forged chunk's subsequent metadata still
- [ ] 3. Free or alloc to trigger the confused walk.
