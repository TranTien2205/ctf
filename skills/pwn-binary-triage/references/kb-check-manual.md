# Manual protection check

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

readelf -h (type=PIE?), readelf -l (GNU_STACK/GNU_RELRO),
readelf -s (__stack_chk_guard, seccomp symbols) - the
protection set is measurable without checksec.

## Pivot

Module read -> the router or sibling module the observation names.
