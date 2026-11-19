# Size positivity checks — can't be too small


Chunk size fields must be >= MINSIZE (0x20 x64) and aligned: a forged
size below the floor or misaligned aborts "invalid size".

## Falsifier

The size you need to forge is below the floor or the alignment can't
be satisfied: that corruption shape is closed.
