# Reading order

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Protections first, then input surface, then the IP-control proof -
the depth file is the last step, not the first. The router's job
is naming which corruption family the binary admits.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
