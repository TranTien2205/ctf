# Safe-linking — the fd mangling (glibc 2.32+) — checklist

Companion to `safe-linking.md`.

## Checklist

- [ ] You can no longer write a raw target address into fd.
- [ ] To aim fd you need: the chunk's own heap address (pos) — i.e. a heap
- [ ] A partially-mangled fd read reveals pos>>12 — a leak of the heap base
- [ ] 1. Leak a heap address (read a fd field, de-mangle with a known
- [ ] 2. mangled_target = (pos >> 12) ^ target.
- [ ] 3. Write mangled_target as fd; the next allocs walk to target.
