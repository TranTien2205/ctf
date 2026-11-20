# Living with seccomp

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

The allowlist names what's left - usually orw
(open/read/write) on the flag path. seccomp_dump
extracts the filter without running the binary.

## Pivot

Module read -> the router or sibling module the observation names.
