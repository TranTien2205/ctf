# Sourcing /bin/sh — the three ways


1. In the binary: `strings -t x ./chal | grep bin` — a fixed address.
2. Planted: write it to .bss via a write gadget or a read() call.
3. In libc: base + the string's known offset — needs the leak.

## The choice

Non-PIE + the string in rodata: use it — the simplest. Else libc's
copy after the leak.
