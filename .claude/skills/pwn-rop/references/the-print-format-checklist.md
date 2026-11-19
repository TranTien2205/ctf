# The print's format — how the leak arrives — checklist

Companion to `the-print-format.md`.

## Checklist

- [ ] puts: raw bytes + newline — the leak is the line minus the newline.
- [ ] write: exactly n bytes — no terminator.
- [ ] printf("%p"): the hex text — parse, don't unpack.
