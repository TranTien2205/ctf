# Protection cell: relro / srop

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Whether `relro` leaves `srop` open.

## Read

The protection's mechanism against the route's requirement -
open, gated (needs a leak/partial), or closed. The cell states
which and why; the triage's measured protection status is the
input.

## Route

Open or gated keeps the route live and names what it needs;
closed removes it - change mechanism layer, not payload
variant.
