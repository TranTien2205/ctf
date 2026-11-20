# ret2csu

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

The __libc_csu_init gadget pair: pop rbx/rbp/r12-r15 then
a call via [r12+rbx*8] - universal gadget in non-PIE
amd64; sets rdi/rsi/rdx through the register chain.

## Pivot

Module read -> the router or sibling module the observation names.
