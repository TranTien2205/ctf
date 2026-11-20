# The format-string leak

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

%p chains read stack memory - canary, saved return,
libc pointers all sit in the format arg range. The
leak comes before the write.

## Pivot

Module read -> the router or sibling module the observation names.
