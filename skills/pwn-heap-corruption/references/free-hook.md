# __free_hook/__malloc_hook — the removed shortcuts


glibc <= 2.34 kept writable hooks: __free_hook = system made the next
free() call system(ptr). Removed in 2.35+ — check the version before
reaching for them.

## The write (<= 2.34)

1. libc leak → __free_hook address.
2. Arbitrary write → __free_hook = system.
3. Free a chunk whose first 8 bytes are "/bin/sh" → system("/bin/sh").

## Alternatives on >= 2.35

- FSOP: corrupt _IO_2_1_* vtables (still reachable).
- environ/exit handlers.
- Direct function-pointer slots the app owns.

## Falsifier

glibc >= 2.35: the symbols don't exist — the addresses don't resolve;
route via FSOP or app-owned pointers.
