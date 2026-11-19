# Heap feng shui — grooming the layout


Heap exploitation is order-sensitive: the sequence of allocs and frees
decides where the target lands. Groom the heap so the corrupted chunk
sits where the write reaches.

## The discipline

- Script the alloc/free sequence; never click through it interactively.
- Fill tcache first (7 frees per size) so later frees hit fastbin/
  unsorted as needed.
- Allocate a guard chunk before an overflow target so the overflow
  hits only the chunk you chose.
- Spray decoy chunks to shape adjacency before a coalescing move.

## The shape

    alloc A(0x90); alloc B(0x90); alloc C(0x90)   # adjacency
    free A; free C                                 # holes around B
    alloc D(0x90)                                  # reuses a hole

## Falsifier

The allocation sizes/counts the program allows can't shape the needed
adjacency: the layout is unreachable — pick a primitive that doesn't
need it.
