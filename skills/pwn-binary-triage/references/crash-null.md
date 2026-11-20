# Crash shape: null/near-null deref

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Fault address near zero - a null or uninit read/write,
not an overflow. Usually unexploitable for IP control;
record and look elsewhere.

## Pivot

Module read -> the router or sibling module the observation names.
