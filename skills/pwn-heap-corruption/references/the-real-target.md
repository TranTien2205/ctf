# Choosing the real target — the endgame


The write lands somewhere that must FIRE: a call slot, a read source,
a gate flag.

## Decision tree

- Hook exists (<=2.34) and reachable → __free_hook = system.
- Hooks gone → FILE vtable (FSOP) or an app-owned function pointer.
- Only a value-write (unsorted attack) → tcache counts or a flag word.
- Only a read → the flag buffer's address.

## Falsifier

Every target's firing condition fails: the write never fires — pick a
slot the program actually touches afterward.
