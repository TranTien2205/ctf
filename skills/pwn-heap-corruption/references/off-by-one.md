# Off-by-one / off-by-NUL — the quiet overlap


A single byte past the chunk clobbers the NEXT chunk's size low byte —
usually P-bit or the size's LSB — enough to forge a bigger chunk.

## The classic (off-by-null)

1. Chunk A (size 0x...8, P set) followed by chunk B.
2. Write A's buffer 1 byte too far → B's size LSB becomes 0x00.
3. B's size drops (e.g. 0x101 → 0x100); its P-bit may clear.
4. Free B: the allocator thinks B's predecessor (A's tail) is free →
   consolidation reaches into live A → overlapping chunks.

## What it buys

Coalescing eats a live allocation → an alloc returns memory a live
object still owns → the overlap primitive everything else builds on.

## Traps

- Needs a controllable next-chunk and a size where the low-byte change
  is meaningful.
- Alignment must keep the forged size sane.

## Falsifier

No byte crosses into the next chunk's size field (bounds-checked write)
— the off-by-one isn't reachable.
