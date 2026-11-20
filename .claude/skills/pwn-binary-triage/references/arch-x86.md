# x86 vs x86-64

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Calling convention changes everything - i386 passes on
stack, amd64 in registers (rdi, rsi, rdx, rcx, r8, r9).
The gadget names differ; the depth file's chains assume
the arch the binary actually is.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
