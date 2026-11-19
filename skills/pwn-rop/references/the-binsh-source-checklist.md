# Sourcing /bin/sh — the three ways — checklist

Companion to `the-binsh-source.md`.

## Checklist

- [ ] 1. In the binary: `strings -t x ./chal | grep bin` — a fixed address.
- [ ] 2. Planted: write it to .bss via a write gadget or a read() call.
- [ ] 3. In libc: base + the string's known offset — needs the leak.
