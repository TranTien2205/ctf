# __free_hook/__malloc_hook — the glibc version bound — checklist

Companion to `fmtstr-hook-glibc-ver.md`.

## Checklist

- [ ] 1. Leak libc — identify the version (strings on the .so, or
- [ ] 2. glibc <= 2.34: __free_hook/__malloc_hook writable, %n writes work.
- [ ] 3. glibc >= 2.35: hooks removed — ret-addr or other slots instead.
- [ ] __free_hook = system → next free(ptr) calls system(ptr) — free a
- [ ] __malloc_hook = one_gadget-ish → next malloc fires it (needs a gadget).
