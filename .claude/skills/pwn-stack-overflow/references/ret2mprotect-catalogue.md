# ret2mprotect — make the stack executable — case catalogue

Can't disable NX but can call mprotect: mark a region RWX, then write and jump to shellcode there.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | NX on, mprotect@plt or in libc | mprotect callable | mprotect the buffer |
| 2 | shellcode written to a known buffer | then jump | two stages |

## Falsifier

Falsifier — mprotect not reachable (no PLT, no leak): can't make a region RWX — stick to ROP/syscall chains.
