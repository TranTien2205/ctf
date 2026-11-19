# The fd/bk pointers on the stack — the free-list boundary — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the overflow reaches heap-adjacent metadata | allocator corruption | pwn-heap-corruption |
| a free then a smash | UAF-adjacent | heap class |

## Falsifier

Falsifier — the corruption reaches heap metadata, not saved state: route to pwn-heap-corruption.
