# The fd/bk pointers on the stack — the free-list boundary

Freed chunk metadata (fd/bk) sits near stack data; smashing into it corrupts the allocator — the stack↔heap boundary.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| the overflow reaches heap-adjacent metadata | allocator corruption | pwn-heap-corruption |
| a free then a smash | UAF-adjacent | heap class |

## Steps

1. If the overflow reaches heap metadata rather than saved registers, it's the heap class's game.
2. fd/bk corruption lets you place a fake chunk — the tcache/fastbin chains live there.
3. Stack-overflow owns the saved-registers path; heap metadata belongs to pwn-heap-corruption.

## Falsifier

Falsifier — the corruption reaches heap metadata, not saved state: route to pwn-heap-corruption.

## Traps

- This boundary decides which class owns the bug.
- A stack smash that hits heap data is unusual — heap is usually a separate region.

## Cross-references

`../pwn-heap-corruption/`
