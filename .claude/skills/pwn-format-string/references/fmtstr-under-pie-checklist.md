# Fmtstr under PIE — every address needs the base — checklist

Companion to `fmtstr-under-pie.md`.

## Checklist

- [ ] 1. Leak a code pointer from the %p dump.
- [ ] 2. base = code_ptr - its_offset.
- [ ] 3. All target addresses = base + offset; write values likewise.
