# Seccomp filter

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Syscall allowlist - execve may be blocked; open/read/write
(orw) is the standard route under a filter. seccomp_dump
reads the filter from the binary.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
