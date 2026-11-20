# Setup cell: system-import / execve-sys

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Whether the `system-import` presence enables the `execve-sys`
route - the binary feature the route requires, measured by
nm/imports/rabin2 rather than assumed.

## Measure

Present enables; absent shifts to the next route in the
family.
