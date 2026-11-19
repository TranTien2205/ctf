# The object table — tracking slots across ops — map

Companion to `the-object-table.md`.

## The ledger
| slot | state after op n | contents |
|---|---|---|
| 0 | alloc → live | object A |
| 1 | free → tcache | stale A bytes |
| 2 | alloc → live | reuses slot-1's chunk |
## Falsifier
