# Partial overwrite mechanics

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Overwriting 1-3 low bytes of an address - preserves ASLR's
high bits; reach limited to +-page but often enough to
land in a useful function.

## Pivot

Module read -> the router or sibling module the observation names.
