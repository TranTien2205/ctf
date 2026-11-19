# The fd/bk pointers on the stack — the free-list boundary — case catalogue

Freed chunk metadata (fd/bk) sits near stack data; smashing into it corrupts the allocator — the stack↔heap boundary.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the overflow reaches heap-adjacent metadata | allocator corruption | pwn-heap-corruption |
| 2 | a free then a smash | UAF-adjacent | heap class |

## Falsifier

Falsifier — the corruption reaches heap metadata, not saved state: route to pwn-heap-corruption.
