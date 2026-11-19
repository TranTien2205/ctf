# tcache_get — the alloc-side take


tcache_get pops the head: reads e->next (de-mangled), clears e->key,
counts-- — the alloc's bin operation.

## The fields read

- entries[i] — the head.
- e->next at user+0x00 — the next head.

## Falsifier

None — the take's mechanics.
