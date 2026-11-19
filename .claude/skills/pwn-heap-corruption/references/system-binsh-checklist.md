# system + /bin/sh — the boring reliable end — checklist

Companion to `system-binsh.md`.

## Checklist

- [ ] libc leak → system's address.
- [ ] A writable call-slot the process will invoke with a string arg.
- [ ] The string: write "/bin/sh" into a freed chunk (whose address is the
- [ ] 1. __free_hook = system; free(chunk starting "/bin/sh").
- [ ] 2. Or: FILE vtable write landing system on a flush call.
