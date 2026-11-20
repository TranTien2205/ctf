# Guard cell: relro / partial-ow

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Whether `relro` blocks, gates, or ignores `partial-ow` -
the protection's mechanism against the route's requirement, and
what the route needs if it is gated rather than open.

## Route

Open keeps it live; gated names the prerequisite (usually a
leak); closed removes it from the plan.
