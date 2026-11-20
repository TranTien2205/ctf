# Setup cell: plt-leakable / orw

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Whether the `plt-leakable` presence enables the `orw`
route - the binary feature the route requires, measured by
nm/imports/rabin2 rather than assumed.

## Measure

Present enables; absent shifts to the next route in the
family.
