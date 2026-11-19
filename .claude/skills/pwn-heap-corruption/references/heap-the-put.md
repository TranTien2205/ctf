# tcache_put — the free-side deposit


free() into tcache runs tcache_put: writes e->next = old_head (mangled
on 2.32+), e->key = tcache, counts++ — the three writes that define
the chunk's bin state.

## The fields

- e->next at user+0x00 — the link (mangled on 2.32+).
- e->key at user+0x08 — the double-free sentinel.

## Falsifier

None — the deposit's mechanics.
