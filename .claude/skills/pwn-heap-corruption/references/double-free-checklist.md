# Double-free — one chunk, freed twice — checklist

Companion to `double-free.md`.

## Checklist

- [ ] glibc <= 2.28 (tcache, no key): plain `free(p); free(p)` works.
- [ ] 2.29+: tcache e->key check — `free(p); free(other); free(p)` cycles,
- [ ] fastbin double-free is checked only against the TOP of the bin —
