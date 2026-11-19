# The P bit — consolidation's switch


P cleared → the previous chunk is treated as free → free() walks
prev_size backward and unlinks it. The whole einherjar/off-by-null
family hangs on this bit.

## The move

1. Clear the next chunk's P (off-by-one into its size LSB).
2. Forge prev_size to point backward at your fake chunk.
3. free() merges backward into the fake → the merged chunk covers your
   memory.

## Falsifier

The byte containing P isn't writable: no consolidation pivot.
