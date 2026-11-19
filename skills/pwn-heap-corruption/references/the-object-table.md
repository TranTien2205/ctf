# The object table — tracking slots across ops


Track every slot's state across the sequence: allocated/freed/
dangling/reused — the table is the exploit's memory.

## The ledger

| slot | state after op n | contents |
|---|---|---|
| 0 | alloc → live | object A |
| 1 | free → tcache | stale A bytes |
| 2 | alloc → live | reuses slot-1's chunk |

Overlaps appear in the table: two live slots pointing at one chunk.

## Falsifier

You can't observe the addresses (no show op): the table must be built
from the known alloc order — first-fit predictability replaces direct
observation.
