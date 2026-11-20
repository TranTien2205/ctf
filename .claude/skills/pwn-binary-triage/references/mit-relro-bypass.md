# Living with RELRO

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Partial RELRO leaves GOT writable; full pushes the
route to __free_hook/__malloc_hook (pre-2.34), saved
return addresses, or stack pivots.

## Pivot

Module read -> the router or sibling module the observation names.
