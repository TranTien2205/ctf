# The constant's location — where the answer sits — checklist

Companion to `the-const-loc.md`.

## Checklist

- [ ] .rodata: a literal constant — read it.
- [ ] .data: initialized writable — read it (and it could be modified).
- [ ] On the stack, built: the build instructions are the answer.
- [ ] In a table: the indexed lookup.
