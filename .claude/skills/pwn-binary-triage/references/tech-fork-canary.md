# Fork canary reuse

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

A forking service keeps the same canary/ASLR per parent -
byte-by-byte brute force becomes viable (256 tries per
byte, 8 bytes). Only valid on fork-per-connection.

## Pivot

Module read -> the router or sibling module the observation names.
