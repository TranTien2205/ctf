# The unsorted-bin leak — libc for free — checklist

Companion to `unsorted-bin-leak.md`.

## Checklist

- [ ] 1. Free a chunk sized > 0x80 (so it skips tcache/fastbin and hits
- [ ] 2. Keep a dangling pointer to it.
- [ ] 3. Read through the dangling pointer: fd/bk = &main_arena.bins[..] —
- [ ] 4. libc_base = leaked - known_offset (offset depends on libc version —
- [ ] Small chunks go to tcache/fastbin, not unsorted — size it right.
- [ ] glibc >= 2.32 tcache holds 7 entries per size — exhaust it (free 7)
