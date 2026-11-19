# heap init — where tcache_perthread lives


The first alloc creates the heap; tcache_perthread_struct is its first
chunk — the struct's position is deterministic (heap_base+0x10).

## Consequence

- The FIRST allocated chunk is the tcache struct — never a user chunk.
- All heap-base arithmetic anchors to it.

## Falsifier

None — a layout fact.
