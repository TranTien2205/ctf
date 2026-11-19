# ret2mprotect — make the stack executable — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| NX on, mprotect@plt or in libc | mprotect callable | mprotect the buffer |
| shellcode written to a known buffer | then jump | two stages |

## Falsifier

Falsifier — mprotect not reachable (no PLT, no leak): can't make a region RWX — stick to ROP/syscall chains.
