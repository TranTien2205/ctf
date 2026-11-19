# tcache key contents — what to write back — checklist

Companion to `the-key-entropy.md`.

## Checklist

- [ ] 1. After the first free, e->key = &tcache_struct.
- [ ] 2. UAF write: set user+8 to 0 (or anything != the struct addr).
- [ ] 3. free() again → key check passes → double-free lands.
