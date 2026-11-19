# Size-field corruption — forging chunk boundaries


Overwrite a chunk's size word via overflow: the allocator now believes
the chunk is bigger (or smaller) than allocated — boundary confusion.

## Outcomes

- Enlarged: the chunk's "end" moves into the neighbor — a free absorbs
  live data (consolidation into overlap).
- Shrunken: free() puts a partial chunk in a bin; the remainder is a
  fake chunk you define.
- Flag bits: clearing P makes prev_size live — consolidation walks
  backward.

## Steps

1. Overflow into the next chunk's size field.
2. Choose the new size so the forged chunk's subsequent metadata still
   parses (the "next" chunk's P and size must look sane).
3. Free or alloc to trigger the confused walk.

## Falsifier

The size field isn't reachable by the bug's write range: metadata
corruption isn't the primitive — check for a data-only write.
