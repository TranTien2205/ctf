# Overlapping chunks — the goal of most grooming


Two live allocations that share memory: the primitive every heap
technique converges to — writes to one corrupt the other.

## Routes to overlap

- Double-free: one chunk allocated twice.
- Off-by-one + consolidate: live chunk eaten by a bigger free chunk.
- Size corruption: a chunk enlarged to cover its neighbor.
- Tcache/fastbin dup: same slot returned twice.

## What the overlap buys

- A "data" object overlapping a "pointer" object → forge a pointer →
  arbitrary read/write.
- A chunk overlapping a freed chunk → control fd/bk directly.

## Verify

After arranging the suspected overlap: write a marker via object A,
read it via object B — the marker proving the alias.

## Falsifier

The two allocations never share memory (distinct addresses survive both
writes): no overlap — the grooming didn't land.
