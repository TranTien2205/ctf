# Leak then static — mixing leaked and fixed addresses — checklist

Companion to `leak-then-static.md`.

## Checklist

- [ ] 1. Leak a code ptr → PIE base → all in-binary addresses known.
- [ ] 2. Leak a libc ptr → libc base → system, /bin/sh, execve.
- [ ] 3. Leak a stack ptr → the ret-addr slot's location.
- [ ] 4. Build every address as base+offset.
