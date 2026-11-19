# Stack smash vs heap metadata — the ownership boundary — case catalogue

Both are 'write past a buffer'; which class owns it depends on WHERE the corruption lands: stack frames belong here, heap chunk metadata belongs to pwn-heap-corruption.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the write reaches saved regs/RIP | stack corruption | this class |
| 2 | the write reaches chunk fd/bk/size | heap corruption | pwn-heap-corruption |
| 3 | the buffer is malloc'd | likely heap class | check where corruption lands |

## Falsifier

Falsifier — the corruption demonstrably lands in heap metadata (a chunk header), not the stack frame: route to pwn-heap-corruption.
