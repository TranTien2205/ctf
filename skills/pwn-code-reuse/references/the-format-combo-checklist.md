# ROP + format-string — the combo — checklist

Companion to `the-format-combo.md`.

## Checklist

- [ ] 1. The %p dump leaks libc/stack/binary pointers.
- [ ] 2. The buffer overflow carries the ROP chain built on those.
- [ ] 3. Or: the %n write IS the chain's delivery.
