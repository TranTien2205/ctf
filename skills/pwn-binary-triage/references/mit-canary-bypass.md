# Living with the canary

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Leak it (format string, info leak, fork-reuse where the
canary stays constant across children) or write around
it (arb-write, heap). Never brute-force blindly on a
non-forking service.

## Pivot

Module read -> the router or sibling module the observation names.
