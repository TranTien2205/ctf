# The very first check — does the class apply? — checklist

Companion to `heap-first-check.md`.

## Checklist

- [ ] A read/write op on an allocated object → yes, the surface exists.
- [ ] A free that leaves a dangling ref → UAF open.
- [ ] An overflow reaching the next chunk's header → metadata corruption
- [ ] A double-free path → dup open.
