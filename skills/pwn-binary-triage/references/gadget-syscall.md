# syscall / int 0x80

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

A raw syscall gadget bypasses libc entirely - the
execve or orw path when symbols are stripped or
seccomp allows it.

## Pivot

Module read -> the router or sibling module the observation names.
