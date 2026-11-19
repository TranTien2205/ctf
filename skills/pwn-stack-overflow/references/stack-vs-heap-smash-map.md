# Stack smash vs heap metadata — the ownership boundary — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the write reaches saved regs/RIP | stack corruption | this class |
| the write reaches chunk fd/bk/size | heap corruption | pwn-heap-corruption |
| the buffer is malloc'd | likely heap class | check where corruption lands |

## Falsifier

Falsifier — the corruption demonstrably lands in heap metadata (a chunk header), not the stack frame: route to pwn-heap-corruption.
