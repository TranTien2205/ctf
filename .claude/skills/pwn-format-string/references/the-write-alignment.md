# Write alignment — the pointer must be arg-aligned


The pointer at a %N$n position must be a complete aligned word — a
4-byte-misaligned pointer writes to the wrong address.

## Steps

1. x64 args are 8-byte slots — the pointer must fill one.
2. If your input bytes place it off-boundary, the deref reads the wrong
   8 bytes.
3. Pad the input so the address lands on an 8-byte boundary.
4. Check alignment with %N$p — it should print YOUR address exactly.

## Falsifier

The pointer can't be aligned at any arg position: the write destination
is unreachable.
