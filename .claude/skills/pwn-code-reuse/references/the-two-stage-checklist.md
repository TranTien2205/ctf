# The two-stage chain — leak then execute — checklist

Companion to `the-two-stage.md`.

## Checklist

- [ ] Stage 1: leak a GOT entry via puts@plt(puts@got); ret to main.
- [ ] Stage 2: with libc base known, the real chain — system("/bin/sh").
