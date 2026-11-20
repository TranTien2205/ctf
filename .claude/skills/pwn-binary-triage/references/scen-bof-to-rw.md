# Scenario: overflow to arb-write

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

The overflow only seeds the chain - the write primitive
comes from a called function (read into a controlled
address), not the overflow itself.

## Pivot

Module read -> the router or sibling module the observation names.
