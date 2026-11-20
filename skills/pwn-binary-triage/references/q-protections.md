# Question: which protections

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

The triage's evidence-backed list: NX, PIE, canary,
RELRO, ASLR inherited from the OS, seccomp if present.
Each one's status changes the route, none is assumed.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
