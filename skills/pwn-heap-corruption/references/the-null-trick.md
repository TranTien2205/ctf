# The null-byte boundary — off-by-null precisely


The off-by-null works because a size like 0x101 → 0x100 changes BOTH
the size (slightly smaller) AND the P-bit (cleared): one byte, two
meanings.

## The two effects

1. Size shrinks: the chunk's end moves back — later metadata sits
   inside "free" space.
2. P clears: prev_size activates — consolidation can walk backward.

## Requirements

- The shrunken size must still be sane (>= MINSIZE, aligned).
- prev_size must be forgeable for the backward walk.

## Falsifier

The byte can't be written as 0 (only non-zero data): the P-bit stays
set — the null-byte family is closed.
