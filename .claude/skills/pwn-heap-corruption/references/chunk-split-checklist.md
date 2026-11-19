# Chunk splitting — the remainder mechanism — checklist

Companion to `chunk-split.md`.

## Checklist

- [ ] 1. Free a large chunk → unsorted/large bin.
- [ ] 2. malloc a smaller size → splits: you get the front, a remainder stays.
- [ ] 3. The remainder chunk's fd/bk and size are heap-resident — reachable
- [ ] A bin-linked chunk adjacent to your allocations → metadata corruption
- [ ] The remainder's fd/bk already point at the arena — a leak source.
