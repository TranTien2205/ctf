# Locating the tcache key field — checklist

Companion to `the-key-offset.md`.

## Checklist

- [ ] 1. Free a chunk → its user area: | e->next | e->key | ...
- [ ] 2. To re-free: overwrite the key (UAF write at user+8) — the double-free
- [ ] 3. The next (fd) field at user+0 — safe-linking mangled on 2.32+.
