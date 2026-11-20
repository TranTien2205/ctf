# Question: which depth file

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Family named -> exactly one depth file: stack, fmtstr,
heap, code-reuse, or rop. The router opens ONE; the
family's boundary modules say when to switch.

## Pivot

Module read -> the router or sibling module the observation names.
