# ARM calling convention

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Args r0-r3; bl/bx returns via lr not a popped pc - the
gadget shapes differ fundamentally (pop {r0, pc} etc.).
qemu-arm-static runs the binary.

## Pivot

Module read -> the router or sibling module the observation names.
