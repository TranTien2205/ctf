# __free_hook/__malloc_hook — the removed shortcuts — checklist

Companion to `free-hook.md`.

## Checklist

- [ ] 1. libc leak → __free_hook address.
- [ ] 2. Arbitrary write → __free_hook = system.
- [ ] 3. Free a chunk whose first 8 bytes are "/bin/sh" → system("/bin/sh").
- [ ] FSOP: corrupt _IO_2_1_* vtables (still reachable).
- [ ] environ/exit handlers.
- [ ] Direct function-pointer slots the app owns.
