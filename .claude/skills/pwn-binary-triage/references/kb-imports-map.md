# The imports map

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

gets/strcpy/scanf/read (unbounded), printf-family
(format), system/exec (easy win), fopen/read (orw),
seccomp_init (filter) - the import list names the bug
families present before any disassembly.

## Pivot

Module read -> the router or sibling module the observation names.
