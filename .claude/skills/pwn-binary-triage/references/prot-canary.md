# Stack canary

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

A checked value before the return address - overflow through
it crashes unless the canary is leaked or the write avoids
it (format string, arb-write). The crash signature names it.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
