# Reading the crash

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

SIGSEGV at a controlled value proves IP control - the fault
address IS the input's reach. A crash at an uncontrolled
address is a different bug (bounds, null deref).

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
