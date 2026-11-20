# amd64 calling convention

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Args in rdi, rsi, rdx, rcx, r8, r9 then stack - the
pop-rdi family of gadgets sets up calls. ret often needed
for 16-byte alignment before libc calls.

## Pivot

Module read -> the router or sibling module the observation names.
