# NX (non-executable stack)

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Stack data is not executable - shellcode on the stack dies,
code reuse (ROP/ret2libc) is the route. The protection names
the family; it does not close the exploit.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
