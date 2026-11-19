# ret2dlresolve notes — the advanced route


When a libc leak is impossible but a call to ANY libc function is
needed: forge the lazy-resolution structures so _dl_runtime_resolve
returns your target.

## The sketch

1. A fake Symbol/Rela/Strtab in writable memory.
2. call _dl_runtime_resolve with a controlled reloc index.
3. The resolver "resolves" to your chosen function.

## Falsifier

Full RELRO removes lazy binding — the resolver never runs; a leak is
mandatory.
