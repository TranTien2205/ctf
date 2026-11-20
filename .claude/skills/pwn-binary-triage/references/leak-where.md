# Where leaks live

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Stack (canary, saved rip, libc), heap (fd/bk of main_arena),
bss (stored pointers), the format arg range - the leak
primitive's reach names which addresses are collectible.

## Pivot

Module read -> the router or sibling module the observation names.
