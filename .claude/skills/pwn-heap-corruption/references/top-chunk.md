# The top chunk — the wilderness


The top chunk is the heap's remainder — every non-binned alloc splits
off it. Its size field is corruption-reachable and its position is
controllable.

## Properties

- Top sits at the heap's end; its size = remaining space.
- A huge fake top size makes the next malloc "allocate" past the heap —
  the house-of-force write.
- Conserving the top: small frees can merge upward into it (clearing
  their P).

## r2 view

`r2 -d ./chal` then `dmh` — the top shows as the last large chunk.

## Falsifier

The top's size field isn't reachable and no alloc can be steered by it
— top-chunk techniques close.
