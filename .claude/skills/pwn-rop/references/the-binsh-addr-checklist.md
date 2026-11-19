# The /bin/sh address — the arg's value — checklist

Companion to `the-binsh-addr.md`.

## Checklist

- [ ] rodata: `strings -t x` offset (non-PIE absolute).
- [ ] .bss: where you planted it.
- [ ] libc: base + str offset.
