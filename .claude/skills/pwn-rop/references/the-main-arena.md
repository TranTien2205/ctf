# main_arena — the heap's anchor


The heap's top structures live in libc's data (main_arena) — a leak
of it gives heap and libc addresses in one shot.

## The use

The unsorted-bin's fd/bk point at main_arena's region — the classic
heap-to-libc leak (see pwn-heap-corruption).
