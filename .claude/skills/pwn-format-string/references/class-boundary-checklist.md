# Class boundary — what format-string is NOT — checklist

Companion to `class-boundary.md`.

## Checklist

- [ ] Shape | Real class
- [ ] a bounded strcpy into a stack buffer | `pwn-stack-overflow`
- [ ] printf("%s", buf) — input is an arg | not a format bug
- [ ] an unbounded copy, not a format | `pwn-stack-overflow`
- [ ] heap metadata corruption | `pwn-heap-corruption`
