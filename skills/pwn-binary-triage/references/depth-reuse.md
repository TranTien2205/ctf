# Route: code reuse

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

NX present, no shellcode - ROP/ret2libc/ret2csu/
one-gadget families in `../../pwn-code-reuse/` and
`../../pwn-rop/`.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
