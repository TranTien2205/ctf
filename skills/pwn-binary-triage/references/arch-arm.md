# ARM/MIPS

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Cross-arch under qemu - the ABI and gadget shapes differ
(bl/bx, lr-as-return); the triage applies but the
depth-file chains are arch-specific.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
