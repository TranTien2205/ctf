# tools/pwn_triage.py first

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

python3 tools/pwn_triage.py <binary> - stdlib-only ELF triage:
protections with the evidence for each, dangerous imports
annotated, essential ROP gadgets, routes each protection leaves.
It reports and ranks; it never claims a bug.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
