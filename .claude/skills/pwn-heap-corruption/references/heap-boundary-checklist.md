# The class boundary — heap vs stack vs index — checklist

Companion to `heap-boundary.md`.

## Checklist

- [ ] Heap corruption: the allocator's state is the target — bins, sizes,
- [ ] Stack overflow: linear buffer → return address — different class
- [ ] OOB index on an object array: the array's neighbors, not the heap —
- [ ] A fmtstr on heap data: the %n write is fmtstr, not heap-corruption —
