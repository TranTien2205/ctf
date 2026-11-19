# Leak then static — mixing leaked and fixed addresses

A PIE binary's addresses move; .rodata strings move with it; libc
addresses move independently. Compose: leak one base, compute all others
from its offsets.

## Steps

1. Leak a code ptr → PIE base → all in-binary addresses known.
2. Leak a libc ptr → libc base → system, /bin/sh, execve.
3. Leak a stack ptr → the ret-addr slot's location.
4. Build every address as base+offset.
