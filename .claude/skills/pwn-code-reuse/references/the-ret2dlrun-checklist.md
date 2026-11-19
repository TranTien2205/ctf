# ret2dlresolve notes — the advanced route — checklist

Companion to `the-ret2dlrun.md`.

## Checklist

- [ ] 1. A fake Symbol/Rela/Strtab in writable memory.
- [ ] 2. call _dl_runtime_resolve with a controlled reloc index.
- [ ] 3. The resolver "resolves" to your chosen function.
