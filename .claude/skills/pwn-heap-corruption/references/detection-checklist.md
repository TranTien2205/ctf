# Detecting heap corruption — the first signals — checklist

Companion to `detection.md`.

## Checklist

- [ ] A crash inside `_int_malloc`, `_int_free`, tcache_put/get — the
- [ ] glibc abort messages: "double free or corruption", "corrupted top
- [ ] A realloc'd object whose fields alias another object's — an overlap.
- [ ] An alloc that returns the same address twice while both are "live".
