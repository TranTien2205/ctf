# Chunk splitting — the remainder mechanism


A large free chunk split by a smaller malloc leaves a remainder — the
remainder's own metadata sits where you can corrupt it.

## Steps

1. Free a large chunk → unsorted/large bin.
2. malloc a smaller size → splits: you get the front, a remainder stays.
3. The remainder chunk's fd/bk and size are heap-resident — reachable
   by your next overflow.

## What it buys

- A bin-linked chunk adjacent to your allocations → metadata corruption
  hits a real bin node.
- The remainder's fd/bk already point at the arena — a leak source.

## Falsifier

No size-gap exists to split: everything is exact-size — the remainder
never forms.
