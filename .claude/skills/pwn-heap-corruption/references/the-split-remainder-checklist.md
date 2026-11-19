# The remainder's metadata — after the split — checklist

Companion to `the-split-remainder.md`.

## Checklist

- [ ] 1. Free big → unsorted; alloc small → remainder.
- [ ] 2. The remainder's fd/bk point at the arena — leaked by reading your
- [ ] 3. Writing them → unsorted-bin corruption.
