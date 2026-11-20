# Gadget cell: leave-ret / i386

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

The `leave-ret` gadget's availability and role on
`i386` - the calling convention it serves and the register it
controls. The triage tool lists what the binary actually
contains.

## Note

Gadget availability is measured on the binary, never assumed
from the architecture's conventions.
