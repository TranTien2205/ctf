# Locating the tcache key field


The key sits in the freed chunk's user area at +0x08 (after e->next at
+0x00) — x64: chunk_user+8; x86: +4.

## Steps

1. Free a chunk → its user area: | e->next | e->key | ...
2. To re-free: overwrite the key (UAF write at user+8) — the double-free
   check reads key==0.
3. The next (fd) field at user+0 — safe-linking mangled on 2.32+.

## Falsifier

The freed chunk isn't in tcache (size class wrong): no key field exists
there — different check applies.
