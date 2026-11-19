# Planting /bin/sh — the three ways


1. Found: the binary's .rodata — `strings ./chal | grep -i bin`.
2. Planted: a write gadget or a read() puts it in .bss at a fixed
   address.
3. From libc: base + the string's known offset.

The chosen way decides the arg's address.
