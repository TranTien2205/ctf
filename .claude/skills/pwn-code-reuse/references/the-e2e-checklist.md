# End to end — a worked example — checklist

Companion to `the-e2e.md`.

## Checklist

- [ ] 1. Offset: 72 (measured).
- [ ] 2. Stage 1: pop rdi; puts@got; puts@plt; ret to main.
- [ ] 3. The print → the resolved puts addr → libc base.
- [ ] 4. Stage 2: pop rdi; binsh_addr; ret; system_addr → shell.
