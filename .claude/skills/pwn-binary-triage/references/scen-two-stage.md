# Scenario: leak-then-return

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Stage 1 leaks and returns to main; stage 2 carries the
real chain - the main-return trick keeps the process
alive between stages.

## Pivot

Module read -> the router or sibling module the observation names.
