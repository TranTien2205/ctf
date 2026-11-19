# Finding /bin/sh — the string source — checklist

Companion to `binsh-source.md`.

## Checklist

- [ ] 1. The binary's own .rodata — `strings ./chal | grep /bin/sh` or
- [ ] 2. libc's copy — base + the string's offset (version-specific).
- [ ] 3. Your planted bytes — write "/bin/sh" into .data/.bss first, then
