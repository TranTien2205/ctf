# Double-free — one chunk, freed twice


Freeing the same chunk twice lands it in a bin twice — two allocations
can then return the same memory → overlapping live objects.

## Version gates

- glibc <= 2.28 (tcache, no key): plain `free(p); free(p)` works.
- 2.29+: tcache e->key check — `free(p); free(other); free(p)` cycles,
  or overwrite the key field, or use a fastbin path.
- fastbin double-free is checked only against the TOP of the bin —
  A-B-A ordering still works.

## What it buys

The same memory allocated to two different objects: one object's write
corrupts the other — a controlled overlap.

## Falsifier

Every duplicate free aborts (tcache key set and checked, fastbin top
check): the route is closed; pivot to a different primitive.
