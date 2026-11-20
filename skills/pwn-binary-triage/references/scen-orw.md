# Scenario: open-read-write

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Seccomp blocking execve - the flag file's path becomes
the payload: open, read into .bss, write to stdout.
The orw chain is the standard seccomp answer.

## Pivot

Module read -> the router or sibling module the observation names.
