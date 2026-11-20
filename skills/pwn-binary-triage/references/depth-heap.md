# Route: heap corruption

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Allocator metadata or object-adjacent corruption -
tcache/dup/consolidate families live in
`../../pwn-heap-corruption/`.

## Pivot

Module read -> the depth file the family names, or the sibling module
answering the protection/reach question.
