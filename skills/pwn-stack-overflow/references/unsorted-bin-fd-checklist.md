# The fd/bk pointers on the stack — the free-list boundary — checklist

Freed chunk metadata (fd/bk) sits near stack data; smashing into it corrupts the allocator — the stack↔heap boundary.

## Checklist

- [ ] If the overflow reaches heap metadata rather than saved registers, it's the heap class's game.
- [ ] fd/bk corruption lets you place a fake chunk — the tcache/fastbin chains live there.
- [ ] Stack-overflow owns the saved-registers path; heap metadata belongs to pwn-heap-corruption.

## Abort conditions

- This boundary decides which class owns the bug.
- A stack smash that hits heap data is unusual — heap is usually a separate region.

## Falsifier

Falsifier — the corruption reaches heap metadata, not saved state: route to pwn-heap-corruption.
